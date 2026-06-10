#!/bin/bash

# Arguments
psql_host=$1
psql_port=$2
db_name=$3
psql_user=$4
psql_password=$5

# Check # of args
if [ "$#" -ne 5 ]; then
  echo "Script expects 5 arguments"
  exit 1
fi

# Get Details
vmstat_mb=$(vmstat --unit M)
hostname=$(hostname -f)
cpu_number=$(lscpu | awk '/^CPU\(s\):/ {print $2}' | xargs)
cpu_architecture=$(lscpu | awk '/^Architecture:/ {print $2}' | xargs)
cpu_model=$(lscpu | awk '/^Model name:/ {$1=$2=""; print $0}' | xargs)
cpu_mhz=$(lscpu | awk '/^Model name:/ {print $NF}' | tr -d 'GHz' | awk '{print $1 * 1000}')
l2_cache=$(lscpu | awk '/^L2 cache:/ {print $3}' | tr -d 'K' | xargs)
total_mem=$(vmstat -s | awk '/total memory/ {print $1}' | xargs)
timestamp=$(vmstat -t | awk '{print $18, $19}' | tail -n1 | xargs)

# INSERT statement
insert_stmt="INSERT INTO host_info(hostname, cpu_number, cpu_architecture, cpu_model, cpu_mhz, l2_cache, timestamp, total_mem)
VALUES('$hostname', '$cpu_number', '$cpu_architecture', '$cpu_model', '$cpu_mhz', '$l2_cache', '$timestamp', '$total_mem')"

export PGPASSWORD=$psql_password
psql -h $psql_host -p $psql_port -d $db_name -U $psql_user -c "$insert_stmt"
exit $?