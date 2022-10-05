/*******************************************************************************
 * BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
 *
 * Copyright (c) 2019-present Barefoot Networks, Inc.
 *
 * All Rights Reserved.
 *
 * NOTICE: All information contained herein is, and remains the property of
 * Barefoot Networks, Inc. and its suppliers, if any. The intellectual and
 * technical concepts contained herein are proprietary to Barefoot Networks, Inc.
 * and its suppliers and may be covered by U.S. and Foreign Patents, patents in
 * process, and are protected by trade secret or copyright law.  Dissemination of
 * this information or reproduction of this material is strictly forbidden unless
 * prior written permission is obtained from Barefoot Networks, Inc.
 *
 * No warranty, explicit or implicit is provided, unless granted under a written
 * agreement with Barefoot Networks, Inc.
 *
 ******************************************************************************/

#include <core.p4>
#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

#include "common/headers.p4"
#include "common/util.p4"

struct digest_t {                                                                 
    PortId_t port;                                                                
    ipv4_addr_t src_ip;
    ipv4_addr_t dst_ip;
    bit<8> protocol;
    bit<16> src_port;
    bit<16> dst_port;
}

struct metadata_t {
	bit<1> assertion_check_2;

	bit<1> assertion_check_3;

	bit<1> assertion_check_1;
	bit<8> BL; 
	PortId_t port;
    	ipv4_addr_t src_ip;
    	ipv4_addr_t dst_ip;
    	bit<8> protocol;
	bit<16> src_port;
 	bit<16> dst_port;
}

// ---------------------------------------------------------------------------
// Ingress parser
// ---------------------------------------------------------------------------
parser SwitchIngressParser(
        packet_in pkt,
        out header_t hdr,
        out metadata_t ig_md,
        out ingress_intrinsic_metadata_t ig_intr_md) {

    TofinoIngressParser() tofino_parser;

    state start {
        tofino_parser.apply(pkt, ig_intr_md);
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select (hdr.ethernet.ether_type) {
            ETHERTYPE_IPV4 : parse_ipv4;
            default : reject;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select (hdr.ipv4.protocol) {
            IP_PROTOCOLS_TCP : parse_tcp;
	    IP_PROTOCOLS_UDP : parse_udp;
            default : reject;
        }
    }
    
    state parse_tcp{
	pkt.extract(hdr.tcp);
	transition accept;	
    }

    state parse_udp{
	pkt.extract(hdr.udp);
	transition accept;	
    }

}
// ---------------------------------------------------------------------------
// Ingress Deparser
// ---------------------------------------------------------------------------
control SwitchIngressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in metadata_t ig_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {
    
    Digest<digest_t>() digest;

    apply {
        if (ig_intr_dprsr_md.digest_type == 1){
		digest.pack({ig_md.port, ig_md.src_ip, ig_md.dst_ip, ig_md.protocol, ig_md.src_port, ig_md.dst_port});
}	
	pkt.emit(hdr);
    }
}

control SwitchIngress(
        inout header_t hdr,
        inout metadata_t ig_md,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {
action assert_check_fail_1(){
	ig_md.assertion_check_1 = 0;
}

 action assert_check_pass_1(){
	ig_md.assertion_check_1 = 1;
}

 	table assert_1_1{
	key = {
		 ig_md.BL : range;
		ig_md.assertion_check_1 : exact;
	}
	actions = {
		assert_check_pass_1;
		assert_check_fail_1;
		NoAction;
	}
	const default_action = assert_check_fail_1;
	const entries = {
		(0x0..0x3,1): assert_check_pass_1();
	
	} 
}

action assert_check_fail_2(){
	ig_md.assertion_check_2 = 0;
}

 action assert_check_pass_2(){
	ig_md.assertion_check_2 = 1;
}

 	table assert_2_2{
	key = {
		 ig_md.BL : range;
		ig_md.assertion_check_2 : exact;
	}
	actions = {
		assert_check_pass_2;
		assert_check_fail_2;
		NoAction;
	}
	const default_action = assert_check_fail_2;
	//const entries = {
//} 
}

	table assert_2_1{
	key = {
		 ig_md.BL :range;
	}
	actions = {
		assert_check_pass_2;
		assert_check_fail_2;
		NoAction;
	}
	const default_action = assert_check_fail_2;
	const entries = {
	0x0..0x1: assert_check_pass_2();
	
	} 
}

action assert_check_fail_3(){
	ig_md.assertion_check_3 = 0;
}

 action assert_check_pass_3(){
	ig_md.assertion_check_3 = 1;
}

 	table assert_3_1{
	key = {
		 ig_md.BL : range;
		ig_md.assertion_check_3 : exact;
	}
	actions = {
		assert_check_pass_3;
		assert_check_fail_3;
		NoAction;
	}
	const default_action = assert_check_fail_3;
	const entries = {
		(0x2..0x3,1): assert_check_pass_3();
	
	} 
}


	action NoAction(){ 
		 ig_md.BL = ig_md.BL + 1; 
	}


    action allow(){
    }
    
    action deny() {
		ig_md.BL = ig_md.BL + 2;
	        ig_intr_dprsr_md.drop_ctl = 0x1; // Drop packet.
    }

    table acl {
        key = {
            hdr.ipv4.src_addr : exact;
            hdr.tcp.src_port : exact;
        }

        actions = {
            allow;
	    deny;
        }

        const default_action = allow;
        size = 1024;
    }
    action rewrite(ipv4_addr_t saddr){
	hdr.ipv4.src_addr=saddr;	    
    }
    table nat {
	key = {
	     hdr.ipv4.src_addr: lpm;
	}
	actions = {
	    rewrite;
	    NoAction;
	 }
	size = 1024;
	}


    apply {
	ig_md.port=ig_intr_md.ingress_port;
	if(hdr.ethernet.ether_type == ETHERTYPE_IPV4){
		ig_md.src_ip=hdr.ipv4.src_addr;
		ig_md.dst_ip=hdr.ipv4.dst_addr;
		ig_md.protocol=hdr.ipv4.protocol;
	}
	if(hdr.ipv4.protocol == IP_PROTOCOLS_TCP){
	  ig_md.src_port=hdr.tcp.src_port;
	  ig_md.dst_port=hdr.tcp.dst_port;
	}
	else{
	  ig_md.src_port=hdr.udp.src_port;
	  ig_md.dst_port=hdr.udp.dst_port;
	}
        
	acl.apply();
	nat.apply();
	
    ig_intr_tm_md.ucast_egress_port = 5;	
	
	ig_intr_dprsr_md.digest_type=1;

        // No need for egress processing, skip it and use empty controls for egress.
        ig_intr_tm_md.bypass_egress = 1w1;
	     
		assert_1_1.apply();
	
 
		assert_2_1.apply();
	
 
		assert_2_2.apply();
	

		if(hdr.ethernet.ether_type!=0x0800){
			assert_check_pass_3();
		}else{
			assert_check_fail_3();
		}
 
		assert_3_1.apply();
	
}
}

Pipeline(SwitchIngressParser(),
         SwitchIngress(),
         SwitchIngressDeparser(),
         EmptyEgressParser(),
         EmptyEgress(),
         EmptyEgressDeparser()) pipe;

Switch(pipe) main;
