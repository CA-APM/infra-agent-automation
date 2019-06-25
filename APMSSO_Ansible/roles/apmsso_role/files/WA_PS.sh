#!/bin/bash
source /etc/profile
if [ "$NETE_WA_ROOT" != "" ]
then
	#echo $NETE_WA_ROOT > /tmp/NETE_WA_ROOT.txt
	echo "NETE_WA_ROOT" > /tmp/output.txt
        echo $NETE_WA_ROOT >> /tmp/output.txt
elif [ "$NETE_PS_ROOT" != "" ]
then
	#echo $NETE_PS_ROOT > /tmp/NETE_PS_ROOT.txt
	echo "NETE_PS_ROOT" > /tmp/output.txt
        echo $NETE_PS_ROOT >> /tmp/output.txt
fi
