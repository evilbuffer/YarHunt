from datetime import datetime, timezone, timedelta
import requests
import os
import zipfile
from config import bazaar_hourly_endpoint, malware_cage, bazaar_zip_name, bazaar_unzip_name, malshare_api_endpoint, malshare_key_one,malshare_key_two, malshare_folder
import shutil
from library.yaralib import scan_directory, create_rule_md5
import time
from apscheduler.schedulers.background import BackgroundScheduler
from library.yaralib import compile_directory
import json

bazaar_last_zip_hash = "placeholder" # simple way to keep track of the last processed batch of files from bazaar

# Setup the needed job store in a global variable
sch = BackgroundScheduler()
sch.damonic = False
sch.start()

def sch_dispatcher():
    # Schedule downloader jobs and job to compile new rules
    sch.add_job(bazaar_process_hourly, "interval", hours=1, id="bazaar_downloader")
    sch.add_job(compile_directory, "interval", minutes=10, id="compile_new_rules")
    sch.add_job(malshare_process_daily, "interval", hours=24, id="malshare_downloader")
    while True:
        alive = 1+1

def get_running_jobs():
    return str(sch.get_jobs())


def bazaar_process_hourly():

    # Create the expected zip file name 
    # There is probably a nicer way to do this
    tz_off = -2.0
    tz_info = timezone(timedelta(hours=tz_off))
    bzr_zip_name = str(datetime.now(tz_info).strftime('%Y-%m-%d-%H.zip'))


    # Download the latest zip file and extract it
    with requests.get(bazaar_hourly_endpoint + bzr_zip_name, stream=True) as reg:
        with open(malware_cage + bazaar_zip_name, "wb") as f:
            for chnk in reg.iter_content(chunk_size=8192):
                f.write(chnk)
    
    bazaar_last_zip_hash = create_rule_md5(malware_cage + bazaar_zip_name)
    with zipfile.ZipFile(malware_cage + bazaar_zip_name, "r") as zfile:
        zfile.extractall(malware_cage + bazaar_unzip_name,pwd="infected".encode("utf-8"))
    # Clean up
    scan_directory(malware_cage + bazaar_unzip_name)
    clean_folder(malware_cage + bazaar_unzip_name)

def malshare_process_daily():
    pe_hashes = []
    pe_plus_hashes = []

    r_pe = requests.get(malshare_api_endpoint + "?api_key={0}&action=type&type=PE32".format(malshare_key_one)) 
    tmp_json = json.loads(r_pe.content)
    for item in tmp_json:
        pe_hashes.append(item["md5"])

    # Now do the same thing for 64 bit PE files
    # Use key two on 64 bit files due to 2000 file download limit on one API key
    r_pe = requests.get(malshare_api_endpoint + "?api_key={0}&action=type&type=PE32+".format(malshare_key_two))
    
    tmp_json = json.loads(r_pe.content)
    for item in tmp_json:
        pe_plus_hashes.append(item["md5"])
    
    for h in pe_hashes:
        with requests.get(malshare_api_endpoint + "?api_key={0}&action=getfile&hash={1}".format(malshare_key_one, h)) as reg:
            with open(malware_cage + h, "wb") as f:
                f.write(reg.content)
    for h in pe_plus_hashes:
        with requests.get(malshare_api_endpoint + "?api_key={0}&action=getfile&hash={1}".format(malshare_key_two, h)) as reg:
            with open(malware_cage + h, "wb") as f:
                f.write(reg.content)
    scan_directory(malware_cage)
    clean_folder(malware_cage)

def clean_folder(path):
    os.remove(malware_cage + bazaar_zip_name)
    for r, d, f in os.walk(path):
        for fi in f:
            os.remove(os.path.join(r,fi))
    try:
        shutil.rmtree(malware_cage + bazaar_unzip_name)
    except FileNotFoundError:
        pass
