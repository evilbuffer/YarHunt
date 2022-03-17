import yara
import os
import hashlib
from config import *
import shutil
from library.webfuncs import post_to_webhook, upload_to_mwdb
from threading import Thread

def create_rule_md5(rule_path):
    return hashlib.md5(open(rule_path,'rb').read()).hexdigest()

def yara_compile_rule(rule_path):
    compiled_rule = yara.compile(rule_path)
    return compiled_rule

def compile_directory():

    compiled_rules_objects = {}
    compiled_present_hashes = []
    noncompiled_hashes = []

    # Prepare the new files
    rules = get_rule_paths(rule_directory)
    for rule in rules:
        noncompiled_hash = create_rule_md5(rule)
        compiled_rules_objects[noncompiled_hash] = yara_compile_rule(rule)
        noncompiled_hashes.append(noncompiled_hash)

    # Check if the files already have been compiled
    present_rules = get_rule_paths(compiled_rules_directory)
    for item in present_rules:
        compiled_present_hashes.append(create_rule_md5(item))
    
    ## Check the difference between the hash sets
    
    tmp_hash_set = set(compiled_present_hashes)
    difference_list = [x for x in noncompiled_hashes if x not in tmp_hash_set]
    
    ## Save the compiled YARA rules
    for i in difference_list:
        compiled_rules_objects[i].save(compiled_rules_directory + i)


def get_rule_paths(rule_dir):
    rules = []
    for root, dir, files in os.walk(rule_dir):
        for f in files:
            rules.append(os.path.join(root, f))
    return rules

def scan_directory(scan_path):
    # Load compiled files
    rule_objects = []
    compiled_rules_path = get_rule_paths(compiled_rules_directory)
    for item in compiled_rules_path:
        rule_objects.append(yara.load(filepath=item))

    # Scan target files
    files_to_be_scanned = get_rule_paths(scan_path)
    for rule in rule_objects:
        for path in files_to_be_scanned:
            print("Scanning {0}".format(path))
            rule_match = rule.match(path,callback=handle_match_callback, which_callbacks=yara.CALLBACK_MATCHES)
            if rule_match:
                # Save the file and send it to MWDB
                handle_matched_file(path, rule_match) 

def handle_matched_file(path, rule_match):    
    with open(rule_match_folder + path.split("/")[-1].split(".")[0], "wb") as dst:
        dst.write(open(path, "rb").read())
    # Might want to just parse the path once and save it, instead of doing this everytime....
    # Add YARA rule name to upload
    upload_to_mwdb(path.split("/")[-1].split(".")[0], rule_match_folder + path.split("/")[-1].split(".")[0])

def handle_match_callback(callback):
    # Call function to notify Discord channel here
    t = Thread(target=post_to_webhook, args=(callback,))
    t.start()
    return yara.CALLBACK_CONTINUE
def get_yara_rules():
    current_rules = []
    for r,d,f in os.walk(rule_directory):
        for fi in f:
            current_rules.append(fi)
    return current_rules
