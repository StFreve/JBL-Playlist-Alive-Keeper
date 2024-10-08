import os
import sys
import argparse
import logging

# Set up logging
log_file = '/var/log/jbl_keeper.log'
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_service_file(args):
    command = f"/usr/bin/python3 {os.path.abspath('main.py')} "
    command += f"--jbl-address {args.jbl_address} "
    if args.jbl_port:
        command += f"--jbl-port {args.jbl_port} "
    if args.jbl_pin:
        command += f"--jbl-pin {args.jbl_pin} "
    if args.pc_address:
        command += f"--pc-address {args.pc_address} "
    if args.interval:
        command += f"--interval {args.interval} "
    if args.additional_args:
        command += f"{' '.join(args.additional_args)}"
    service_content = f"""[Unit]
Description=JBL Keeper Service
After=network.target

[Service]
ExecStart={command}
Restart=always
User={args.user}
StandardOutput=append:{log_file}
StandardError=append:{log_file}

[Install]
WantedBy=multi-user.target
"""
    return service_content

def setup_service(args):
    service_content = create_service_file(args)
    service_path = '/etc/systemd/system/jbl_keeper.service'
    
    try:
        with open(service_path, 'w') as f:
            f.write(service_content)
        logging.info(f"Service file created at {service_path}")
        
        os.system('sudo systemctl daemon-reload')
        os.system('sudo systemctl enable jbl_keeper.service')
        os.system('sudo systemctl start jbl_keeper.service')
        logging.info("JBL Keeper service has been enabled and started.")
        print(f"JBL Keeper service has been set up. Check {log_file} for logs.")
    except PermissionError:
        logging.error("Unable to create service file. Please run this script with sudo.")
        print(f"Error: Unable to create service file. Please run this script with sudo. Check {log_file} for details.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup JBL Keeper Service")
    parser.add_argument('--pc-address', help="IP address of the PC (optional). If you are running the script on the same machine where the JBL speaker is connected, you can ignore this option.")
    parser.add_argument('--jbl-address', required=True, help="IP address of the JBL speaker")
    parser.add_argument('--jbl-port', type=int, help="Port of the JBL speaker (default: 80)")
    parser.add_argument('--jbl-pin', type=int, help="PIN of the JBL speaker (default: 1234)")
    parser.add_argument('--user', default=os.getlogin(), help="User to run the service (default: current user)")
    parser.add_argument('--interval', type=int, help="Interval to send keep alive requests (default: 60)")
    parser.add_argument('additional_args', nargs=argparse.REMAINDER, help="Additional arguments for main.py")
    
    args = parser.parse_args()
    setup_service(args)
