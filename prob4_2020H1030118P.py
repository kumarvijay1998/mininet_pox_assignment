# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#ys11
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
from pox.openflow.of_json import *
from pox.lib.recoco import Timer
import time
log = core.getLogger()
src_dpid = 0
dst_dpid = 0
input_pkts=0
output_pkts=0
input_pkts1=0
output_pkts1=0
def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

def getTheTime():  #fuction to create a timestamp
  flock = time.localtime()
  then = "[%s-%s-%s" %(str(flock.tm_year),str(flock.tm_mon),str(flock.tm_mday))
  if int(flock.tm_hour)<10:
    hrs = "0%s" % (str(flock.tm_hour))
  else:
    hrs = str(flock.tm_hour)
  if int(flock.tm_min)<10:
    mins = "0%s" % (str(flock.tm_min))
  else:
    mins = str(flock.tm_min)
  if int(flock.tm_sec)<10:
    secs = "0%s" % (str(flock.tm_sec))
  else:
    secs = str(flock.tm_sec)
  then +="]%s.%s.%s" % (hrs,mins,secs)
  return then

def _handle_flowstats_received (event):
   global src_dpid, dst_dpid, input_pkts, output_pkts,input_pkts1,output_pkts1
   for f in event.stats:
     if f.match.nw_dst==IPAddr("10.0.0.4") and (f.match.tp_dst==80 or f.match.tp_src==80) and event.connection.dpid==src_dpid:
       if f.packet_count>0:
         input_pkts1=f.packet_count
     if f.match.nw_dst==IPAddr("10.0.0.4") and (f.match.tp_dst==80 or f.match.tp_src==80) and event.connection.dpid==dst_dpid:
       output_pkts1 = f.packet_count
       if input_pkts1>0:
         print "Path Loss Rate For Http Traffic =", (input_pkts1-output_pkts1)*1.0/input_pkts*100,"%"

  
   
     #packet loss for non http traffic
     if f.match.nw_dst==IPAddr("10.0.0.4") and event.connection.dpid==src_dpid:
       if f.packet_count>0:
         input_pkts=f.packet_count
     if f.match.nw_dst==IPAddr("10.0.0.4")  and event.connection.dpid==dst_dpid:
       output_pkts = f.packet_count
       if input_pkts>0:
         print "Path Loss Rate For Non- Traffic =", (input_pkts-output_pkts)*1.0/input_pkts*100
    
def _handle_ConnectionUp (event):
  global src_dpid, dst_dpid
  print "ConnectionUp: ", dpidToStr(event.connection.dpid)
  for m in event.connection.features.ports:
    if m.name == "s1-eth3":
      src_dpid = event.connection.dpid
    elif m.name == "s4-eth4":
      dst_dpid = event.connection.dpid
  field1,value1= core.openflow.connections.items()[0]
  field2,value2= core.openflow.connections.items()[1]
  field3,value3= core.openflow.connections.items()[2]
  field4,value4= core.openflow.connections.items()[3]
  ip_h3=IPAddr("10.0.0.3")
  ip_h1=IPAddr("10.0.0.1")
  ip_h2=IPAddr("10.0.0.2")
  ip_h4=IPAddr("10.0.0.4")
#question 2 rules 
   #to handle arp because initially ARP packets are sent and then  only 
    #packets corresponding to ip destinations are sent
  fm=of.ofp_flow_mod()
   # fm.match.in_port=1
  fm.match.dl_type=0x0806
    #fm.actions.append(of.ofp_action_output(port=4))
  fm.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
  value1.send(fm)
  fm=of.ofp_flow_mod()
    #fm.match.in_port=4
  fm.match.dl_type=0x0806
    #fm.actions.append(of.ofp_action_output(port=1))
  fm.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
  value1.send(fm)
  fm=of.ofp_flow_mod()
  fm.match.in_port=1
  fm.match.dl_type=0x0806
  fm.actions.append(of.ofp_action_output(port=2))
    #fm.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
  value3.send(fm)
  fm=of.ofp_flow_mod()
  fm.match.in_port=2
  fm.match.dl_type=0x0806
  fm.actions.append(of.ofp_action_output(port=1))
    #fm.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
  value3.send(fm)
  fm=of.ofp_flow_mod()
    #fm.match.in_port=4
  fm.match.dl_type=0x0806
  #fm.actions.append(of.ofp_action_output(port=2))
  fm.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
  value4.send(fm)
  fm=of.ofp_flow_mod()
    #fm.match.in_port=2
  fm.match.dl_type=0x0806
    #fm.actions.append(of.ofp_action_output(port=4))
  fm.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
  value4.send(fm)
         #above rules are for s3
         #to handle s2 arp packets
  fm=of.ofp_flow_mod()
  fm.match.in_port=1
  fm.match.dl_type=0x0806
  fm.actions.append(of.ofp_action_output(port=2))
  value2.send(fm)
  fm=of.ofp_flow_mod()
  fm.match.in_port=2
  fm.match.dl_type=0x0806
  fm.actions.append(of.ofp_action_output(port=1))
  value2.send(fm)
    #End for the ARP Rules for basic connectivity and now IP rules will take command
    
      

  rule17=of.ofp_flow_mod()
  rule17.match.dl_type=0x800
  rule17.match.in_port=1
  rule17.priority=110
  rule17.match.nw_proto=6
  rule17.match.nw_src=ip_h1
  rule17.match.nw_dst=ip_h4
  rule17.match.tp_src=80
  rule17.actions.append(of.ofp_action_output(port=3))
  value1.send(rule17)

  #rules for switch s1
    #to route traffic h2 from h3 via s3
  rule50=of.ofp_flow_mod()
  rule50.match.dl_type=0x0800
  rule50.match.nw_src=ip_h2
  rule50.match.nw_dst=ip_h3
  rule50.actions.append(of.ofp_action_output(port=4))
  value1.send(rule50)
  rule50=of.ofp_flow_mod()
  rule50.match.dl_type=0x0800
    #rule50.match.nw_src=ip_h2
  rule50.match.nw_dst=ip_h2
  rule50.actions.append(of.ofp_action_output(port=2))
#  value1.send(rule50)
  rule17=of.ofp_flow_mod()
  rule17.match.dl_type=0x800
  rule17.match.in_port=2
  rule17.priority=99
  rule17.match.nw_proto=6
  rule17.match.nw_src=ip_h4
  rule17.match.nw_dst=ip_h1
  rule17.match.tp_src=80
  rule17.actions.append(of.ofp_action_output(port=3))
  value4.send(rule17)#it is rule for s4
    #to handle http send h1 traffice which destined to h4 via s2
  rule17=of.ofp_flow_mod()
  rule17.match.dl_type=0x800
  rule17.match.in_port=1
  rule17.priority=100
  rule17.match.nw_proto=6
  rule17.match.nw_src=ip_h1
  rule17.match.nw_dst=ip_h4
  rule17.match.tp_dst=80
  rule17.actions.append(of.ofp_action_output(port=3))
  value1.send(rule17)
  rule17=of.ofp_flow_mod()
  rule17.match.dl_type=0x800
  rule17.match.in_port=2
  rule17.priority=110
  rule17.match.nw_proto=6
  rule17.match.nw_src=ip_h4
  rule17.match.nw_dst=ip_h1
  rule17.match.tp_dst=80
  rule17.actions.append(of.ofp_action_output(port=3))
  value4.send(rule17)
     #for non http traffic b/w h1 h4 forward via s3
  rule4=of.ofp_flow_mod()
  rule4.match.in_port=1
  rule4.match.dl_type=0x0800
  rule4.match.nw_dst=ip_h4
  rule4.match.nw_src=ip_h1
  rule4.priority=95
  rule4.actions.append(of.ofp_action_output(port=4))
  value1.send(rule4)
    #rule to receive traffic and send to h1 and h2
  rule13=of.ofp_flow_mod()
  rule13.match.dl_type=0x0800
  rule13.match.nw_dst=ip_h1
    #rule13.match.in_port=4
  rule13.actions.append(of.ofp_action_output(port=1))
  value1.send(rule13)
       #to send to h2
  rule14=of.ofp_flow_mod()
  rule14.match.dl_type=0x0800
  rule14.match.nw_dst=ip_h2
  rule14.actions.append(of.ofp_action_output(port=2))
 #rules for switch s2
  rule6=of.ofp_flow_mod()
  rule6.match.in_port=1
  rule6.actions.append(of.ofp_action_output(port=2))
  value2.send(rule6)
    #rule for traffic which come from s4
  rule11=of.ofp_flow_mod()
  rule11.match.in_port=2
  rule11.actions.append(of.ofp_action_output(port=1))
  value2.send(rule11)
 #rules for switch s3
    #rule for traffic which come from s1
  rule8=of.ofp_flow_mod()
  rule8.match.in_port=1
  rule8.actions.append(of.ofp_action_output(port=2))
  value3.send(rule8)
  #rule for traffic which come from s4
  rule12=of.ofp_flow_mod()
  rule12.match.in_port=2
  rule12.actions.append(of.ofp_action_output(port=1))
  value3.send(rule12)
 #ules for switch s4
   #rule for traffic which is destined to h3
  rule51=of.ofp_flow_mod()
  rule51.match.dl_type=0x0800
  rule51.match.nw_dst=ip_h3
  rule51.actions.append(of.ofp_action_output(port=1))
  value4.send(rule51)
  rule51=of.ofp_flow_mod()
  rule51.match.dl_type=0x0800
  rule51.match.nw_src=ip_h3
  rule51.match.nw_dst=ip_h2
  #rule51.actions.append(of.ofp_action_output(port=4))
 # value4.send(rule51)
     #to handle http traffic bw h4 h1 via s2
  rule18=of.ofp_flow_mod()
  rule18.match.dl_type=0x800
  rule18.match.in_port=2
  rule18.priority=100
  rule18.match.nw_proto=6
  rule18.match.nw_src=ip_h4
  rule18.match.nw_dst=ip_h1
  rule18.match.tp_src=80
  rule18.actions.append(of.ofp_action_output(port=3))
  value4.send(rule18)
     #to handle incoming traffic from s2 for http
  rule19=of.ofp_flow_mod()
  rule19.match.dl_type=0x800
  rule19.match.in_port=3
  rule19.priority=100
  rule19.match.nw_proto=6
  rule19.match.nw_src=ip_h1
  rule19.match.nw_dst=ip_h4
  rule19.match.tp_dst=80
  rule19.actions.append(of.ofp_action_output(port=2))
  value4.send(rule19)

    
     #to handle non http traffic
  rule15=of.ofp_flow_mod()
  rule15.match.dl_type=0x0800
  rule15.match.in_port=4
  rule15.match.nw_dst=ip_h4
  rule15.actions.append(of.ofp_action_output(port=2))
  value4.send(rule15)
    
  rule4=of.ofp_flow_mod()
  rule4.match.in_port=2
  rule4.match.dl_type=0x0800
  rule4.match.nw_dst=ip_h1
  rule4.match.nw_src=ip_h4
  rule4.priority=90
  rule4.actions.append(of.ofp_action_output(port=4))
  value4.send(rule4)

      #for traffic which destined to h4
  rule52=of.ofp_flow_mod()
  rule52.match.dl_type=0x0800
  rule52.match.nw_dst=ip_h4
  rule52.actions.append(of.ofp_action_output(port=2))
  value4.send(rule52)
  rule52=of.ofp_flow_mod()
  rule52.match.dl_type=0x0800
  rule52.match.nw_dst=ip_h2
  rule52.actions.append(of.ofp_action_output(port=3))
#  value4.send(rule52)
  log.debug("Rules pushed successfully")
  
def launch ():
  core.openflow.addListenerByName("FlowStatsReceived",_handle_flowstats_received)
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
  Timer(1, _timer_func, recurring=True)
