/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

//My includes
// #include "include/headers.p4"
// #include "include/parsers.p4"

#define N_PREFS 1024
#define PORT_WIDTH 32
#define N_PORTS 512

#define N_PREFS 1024
#define PORT_WIDTH 32
#define N_PORTS 512
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<20> label_t;
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}
header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<2>    ecn;
    bit<6>    dscp;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}
struct metadata {
	bit<1> assertion_check_1;
	bit<8> BL; 
    bit<2> meter_color;
    bit<1> linkState;
    bit<32> nextHop;
    bit<32> index;
}
struct headers {
    ethernet_t                      ethernet;
    ipv4_t                          ipv4;
}
/*************************************************************************
*********************** P A R S E R  *******************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {

        transition parse_ethernet;

    }

    state parse_ethernet {

        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            0x0800: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }

}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);

    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
action assert_check_fail_1(){
	meta.assertion_check_1 = 0;
}

 action assert_check_pass_1(){
	meta.assertion_check_1 = 1;
}

 	table assert_1_1{
	key = {
		 meta.BL : exact;
	}
	actions = {
		assert_check_pass_1;
		assert_check_fail_1;
		NoAction;
	}
	const default_action = assert_check_fail_1;
	const entries = {
	0x0..0x1: assert_check_pass_1();
	0x4..0x5: assert_check_pass_1();
	
	} 
}


    // Register to look up the port of the default next hop.
    register<bit<PORT_WIDTH>>(N_PREFS) primaryNH;
    register<bit<PORT_WIDTH>>(N_PREFS) alternativeNH; 

    // Register containing link states. 0: No Problems. 1: Link failure.
    // This register is updated by CLI.py, you only need to read from it.
    register<bit<1>>(N_PORTS) linkState;

    action rewriteMac(macAddr_t dstAddr){
		 meta.BL = meta.BL + 1;
	    hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
	}

    action ipv4_drop() {
		 meta.BL = meta.BL + 4;
        mark_to_drop(standard_metadata);
    }
    action rewrite_drop() {
        mark_to_drop(standard_metadata);
    }

    action read_port(bit<32>  index){
        meta.index = index;
        // Read primary next hop and write result into meta.nextHop.
        primaryNH.read(meta.nextHop,  meta.index);
        
        //Read linkState of default next hop.
       linkState.read(meta.linkState, meta.nextHop);
    }

    action read_alternativePort(){
        //Read alternative next hop into metadata
        alternativeNH.read(meta.nextHop, meta.index);
    }


    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            read_port;
            ipv4_drop;
        }
        size = 512;
        default_action = ipv4_drop;
    }

    table rewrite_mac {
        key = {
             meta.nextHop: exact;
        }
        actions = {
            rewriteMac;
            rewrite_drop;
        }
        size = 512;
        default_action = rewrite_drop;
    }
    
    apply {
        if (hdr.ipv4.isValid()){
            ipv4_lpm.apply();

            if (meta.linkState > 0){
                read_alternativePort();
            }

            // Do not change the following lines: They set the egress port
            // and update the MAC address.
            standard_metadata.egress_spec = (bit<9>) meta.nextHop;
		    rewrite_mac.apply();
	meta.BL = meta.BL + 2;
    
        }
    
		assert_1_1.apply();
	

		if(meta.linkState>0){
			assert_check_pass_1();
		}else{
			assert_check_fail_1();
		}
}
}
/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    apply {

    }

}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
  update_checksum(
      hdr.ipv4.isValid(),
            { hdr.ipv4.version,
        hdr.ipv4.ihl,
              hdr.ipv4.dscp,
              hdr.ipv4.ecn,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}




/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
