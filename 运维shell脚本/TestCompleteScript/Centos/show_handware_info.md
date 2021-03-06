```shell
#!/bin/bash
########## ===== Notice ===== ##########
# Script Name: Config_VMHost_Network_Rhel7
# Script Version : 1.02
# Update Date : 2018-03-27
# Description : VMHost初始化配置网络、主机名。

#####################  Initial  #####################

HOST_NAME=""
NETWORK_IP=""
NETWORK_GATEWAY=""
NETWORK_NETMASK=""
GATEWAY_CUSTOM=""
NETMASK_CUSTOM=""
NETMASK_DEFAULT="255.255.255.0"

#####################  Read Config #####################

echo "Please input hostname here:"
read HOST_NAME
if [ -z $HOST_NAME ];then
	echo "Hostname will not be changed."
fi
echo "Please input IP address here:"
read NETWORK_IP
if [ -z $NETWORK_IP ];then
	echo "You need input IP here. Please try again."
	exit
fi
echo "Please input Gateway here : "
read GATEWAY_CUSTOM
if [ -z $GATEWAY_CUSTOM  ];then
	echo "You need input GATEWAY here. Please try again."
        exit
else 
	NETWORK_GATEWAY=$GATEWAY_CUSTOM
fi
echo "Please input Netmask here (Default is $NETMASK_DEFAULT):"
read NETMASK_CUSTOM
if [ -z $NETMASK_CUSTOM ];then 
	NETWORK_NETMASK=$NETMASK_DEFAULT
else 
	NETWORK_NETMASK=$NETMASK_CUSTOM
fi

#######################  Modify Cofiguration  ########################

sed -i '/^ONBOOT/s/=.*/=yes/' /etc/sysconfig/network-scripts/ifcfg-ens192
sed -i '/^BOOTPROTO/s/=.*/=none/' /etc/sysconfig/network-scripts/ifcfg-ens192
sed -i '/^IPADDR/d' /etc/sysconfig/network-scripts/ifcfg-ens192
sed -i '/^NETMASK/d' /etc/sysconfig/network-scripts/ifcfg-ens192
sed -i '/^GATEWAY/d' /etc/sysconfig/network-scripts/ifcfg-ens192
echo "IPADDR=$NETWORK_IP
NETMASK=$NETWORK_NETMASK
GATEWAY=$NETWORK_GATEWAY">> /etc/sysconfig/network-scripts/ifcfg-ens192
echo "DNS1=10.8.6.10" >> /etc/sysconfig/network-scripts/ifcfg-ens192
echo "DNS2=172.17.0.10" >> /etc/sysconfig/network-scripts/ifcfg-ens192

echo $HOST_NAME > /etc/hostname
hostname $HOST_NAME

systemctl restart network
```

