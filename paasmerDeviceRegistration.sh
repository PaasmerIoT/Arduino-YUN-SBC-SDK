#!/bin/bash

path=`pwd`

echo `rm -rf $path/PAASMER-IoT-Arduino-Yun-Library/examples/BasicPubSub/details.h`

getting_unique()
{
realcounts=$(curl --data "deviceName="$devicename"&email="$username"" http://ec2-52-41-46-86.us-west-2.compute.amazonaws.com/paasmerv2DevAvailability_develop.php)
#echo $realcounts
if [ $realcounts = "devicename_accepted" ]
then
        echo "accepted"
elif [ $realcounts = "user_not_registered" ]
then
#       echo $realcounts
        exit
elif [ $realcounts = "devicename_already_there_for_this_user" ]
then
#else
        echo "devicename already exist"
        read -r -p "Do you want to continue with another device name? [yes/no] " status
        echo " "
        echo $status
        if [ $status = "yes" ]
        then
                getting_devicename
        else
                exit
        fi
fi
}

getting_devicename ()
{
read -r -p "Please enter the device name you want:[alphanumeric only(a-z A-Z 0-9)] " devicename
echo $devicename
if [ ${#devicename} != 0 ]
then
        getting_unique
else
        getting_devicename
fi
}

getting_username()
{
read -r -p "Please enter your paasmer registered email id " username
echo $username
if [ ${#username} != 0 ]
then
        usercount=$(curl --data "UserName="$username"" http://ec2-52-41-46-86.us-west-2.compute.amazonaws.com/paasmerv2UserVerify.php)
#       echo $usercount
        if [ $usercount = 1 ]; then
                echo "UserName exists, Please proceed with Device regsitration"
                getting_devicename
        else
                echo "User is not Registered"
                echo " "
                echo "Please Register to our PaasmerIoT platform at https://dashboard.paasmer.co/"
                exit
        fi
else
        getting_username
fi
}

getting_username
thingname=`uuid`
echo "#define UserName \"$username\"" >> /$path/PAASMER-IoT-Arduino-Yun-Library/examples/BasicPubSub/details.h
echo "#define DeviceName \"$devicename\"" >> /$path/PAASMER-IoT-Arduino-Yun-Library/examples/BasicPubSub/details.h
echo "#define ThingName \"$thingname\"" >> /$path/PAASMER-IoT-Arduino-Yun-Library/examples/BasicPubSub/details.h
 

cat > .Install.log << EOF3
Logfile for Installing Paasmer...
EOF3

logname=$(who | awk '{print $1}');

echo $path >> .Install.log
user=$(echo $USER)
user='/home/'$user
echo $user >> .Install.log
echo "--> Installing...\n" >> .Install.log
sudo chmod -R 777 ./*

echo "--> Installing requerments......." >> .Install.log


sudo pip install awscli
echo "Configuring data..." >> .Install.log

sudo mkdir -p /root/.aws
sudo chmod -R 777 /root/.aws
sudo mkdir -p $path/PAASMER-IoT-Python-Runtime/certs
sudo chmod -R 777 $path/PAASMER-IoT-Python-Runtime/certs

cat > /root/.aws/config << EOF1
[default]
region = us-west-2
EOF1
echo "U2FsdGVkX1+WF++BqX9N+Bfu/jsDgfM9rxd77LO3I8xVxgLBbNmglZprOCtcyvJs
Jteh6FPrLMKb4r8uSq6C/w==" > .old.txt
accesskey=$(cat .old.txt | openssl enc -aes-128-cbc -a -d -salt -pass pass:asdfghjkl);

keyid=$(echo "U2FsdGVkX19XbOtwglyiBxjyEME74FjnlS5KrbdvXHQGbUC/BulYsgg+a35BR64W" | openssl enc -aes-128-cbc -a -d -salt -pass pass:asdfghjkl);

echo "[default]
aws_secret_access_key = $accesskey
aws_access_key_id = $keyid
" > /root/.aws/credentials



endpoint=$(sudo su - root -c"aws iot describe-endpoint" | grep "endpoint" | awk '{print $2}');
echo $endpoint >> .Install.log

touch $path/PAASMER-IoT-Python-Runtime/certs/output.txt

PAASMER=$devicename;
echo $PAASMER >> .Install.log
Thingjson=$(sudo su - root -c "aws iot create-thing --thing-name $thingname");
echo $Thingjson >> .Install.log
echo " Thing Json is "
echo $Thingjson | grep "thingArn" | awk '{print $38}'
data=$(sudo cat $path/.Install.log | grep "thingArn" | awk '{print $3'} | tr -d ',')
echo $data
echo "#define ThingArn $data" >> $path/PAASMER-IoT-Arduino-Yun-Library/examples/BasicPubSub/details.h
touch $path/PAASMER-IoT-Python-Runtime/certs/output.txt
sudo su - root -c "aws iot create-keys-and-certificate --set-as-active --certificate-pem-outfile $path/PAASMER-IoT-Python-Runtime/certs/$PAASMER-certificate.pem.crt --public-key-outfile $path/PAASMER-IoT-Python-Runtime/certs/$PAASMER-public.pem.key --private-key-outfile $path/PAASMER-IoT-Python-Runtime/certs/$PAASMER-private.pem.key" > $path/PAASMER-IoT-Python-Runtime/certs/output.txt

sudo chmod -R 777 ./*
cat $path/PAASMER-IoT-Python-Runtime/certs/output.txt >> .Install.log

out=$(sudo cat $path/PAASMER-IoT-Python-Runtime/certs/output.txt | grep "certificateArn" | awk '{print $2}')


ARN=$(echo $out | sed 's/,$//')
echo $ARN >> .Install.log
echo " the ARN is "
echo $ARN
sudo su - root -c "aws iot create-policy --policy-name $thingname --policy-document '{ \"Version\": \"2012-10-17\", \"Statement\": [{\"Action\": [\"iot:*\"], \"Resource\": [\"*\"], \"Effect\": \"Allow\" }] }'" >> .Install.log




sudo su - root -c "echo \"alias PAASMER_THING='sudo aws iot attach-thing-principal --thing-name $thingname --principal $ARN'\" >> /root/.bashrc"
sudo su - root -c "echo \"alias PAASMER_POLICY='sudo aws iot attach-principal-policy --policy-name $thingname --principal $ARN'\" >> /root/.bashrc"
echo "Added to PAASMER alias...\n" >> .Install.log




sudo chmod -R 777 ./*

echo "************************************************************"
echo "-----------------------------------------------------------"
echo "-->  Run below commands.."
echo "-->  1) sudo su "
echo "-->  2) source ~/.bashrc "
echo "-->  3) PAASMER_THING "
echo "-->  4) PAASMER_POLICY "
echo "-->  5) sed -i 's/alias PAASMER/#alias PAASMER/g' ~/.bashrc "
echo "-->  6) exit "

echo "**************************************************************";
echo "After device registration, edit the config file with credentials and feed details"

echo "File Transfered successfully...." >> .Install.log
sudo chmod 777 ./*
echo $PAASMER >> .Install.log

