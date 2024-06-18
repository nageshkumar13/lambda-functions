import boto3
import datetime
import logging
import os

# Initialize Boto3 client for EC2
ec2 = boto3.client('ec2')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add a console handler to ensure logs are output to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
if not logger.handlers:
    logger.addHandler(console_handler)

def get_ami_using_snapshot(snapshot_id):
    images = ec2.describe_images(Owners=['self'])['Images']
    for image in images:
        for bd_mapping in image.get('BlockDeviceMappings', []):
            ebs = bd_mapping.get('Ebs', {})
            if ebs.get('SnapshotId') == snapshot_id:
                return image['ImageId']
    return None


def lambda_handler(event, context):
    # Get the current date and time in UTC    
    current_datetime = datetime.datetime.now(datetime.timezone.utc)
    #print(current_datetime)    
    
    # Format the date as YYYY-MM-DD
    date_string = current_datetime.strftime('%Y-%m-%d')
    #print(date_string)

    # Get a list of all snapshots in your AWS account
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    # Create a list of attached volume IDs
    attached_volume_ids = []

    # Iterate through instances and collect attached volume IDs
    reservations = ec2.describe_instances()['Reservations']
    # print(reservations)
    for reservation in reservations:
        for instance in reservation.get('Instances', []):
            #print(instance)    
            block_device_mappings = instance.get('BlockDeviceMappings', [])
            #print(block_device_mappings)
            for mapping in block_device_mappings:                
                ebs = mapping.get('Ebs', {})
                #print(mapping)
                volume_id = ebs.get('VolumeId')
                #print(volume_id)
                if volume_id:
                    attached_volume_ids.append(volume_id)
    #print(attached_volume_ids)    

    # Create a set of unique attached volume IDs
    attached_volume_ids_set = set(attached_volume_ids)
    #print(attached_volume_ids_set)
    #logger.info("Volume ID's attached to EC2 instances : %s", attached_volume_ids_set)   
    
    #logger.info("Starting lambda execution : %s", date_string)

    # Handle snapshot deletions or other cleanup
    try:
        # Example: deleting snapshots (you should define how you collect snapshots)
        snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
        
        for snapshot in snapshots:
            snapshot_id = snapshot['SnapshotId']
            volume_id = snapshot['VolumeId']
            logger.info("Snapshot on AWS account: %s", snapshot_id)
            logger.info("Snapshot volume ID: %s", volume_id)
            logger.info("Attached volume IDs: %s", attached_volume_ids_set)
            
            if volume_id not in attached_volume_ids_set:
                # Check if the snapshot is used by any AMI
                ami_id = get_ami_using_snapshot(snapshot_id)
                if ami_id:
                    logger.warning("Snapshot %s is in use by AMI %s, skipping deletion.", snapshot_id, ami_id)
                else:
                    # Attempt to delete the snapshot
                    try:
                        logger.info("Deleting snapshot %s from volume %s", snapshot_id, volume_id)
                        ec2.delete_snapshot(SnapshotId=snapshot_id)
                        logger.info("Deleted snapshot: %s", snapshot_id)
                    except ec2.exceptions.ClientError as e:
                        if 'InvalidSnapshot.InUse' in str(e):
                            logger.warning("Snapshot %s is in use, skipping deletion.", snapshot_id)
                        else:
                            raise

    except Exception as e:
        logger.error("An error occurred during snapshot deletion: %s", e)


