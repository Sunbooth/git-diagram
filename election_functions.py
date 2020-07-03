
from genericpath import isfile
import hashlib
import json
import requests
from os import mkdir
from os.path import isdir, isfile
from hashlib import sha256

election_codes = {
    "2010": 382037,
    "2015": 382386,
    "2017": 730039
}


def fetch_data_for_election(election_id):
    url = "http://lda.data.parliament.uk/electionresults.json?electionId=" + str(election_id) + "&_pageSize=650"
    response = requests.get(url).json()
    curated_json = {}
    for i in response["result"]["items"]:
        current_con = i["constituency"]["label"]["_value"]
        current_con_code = i["_about"].split("/")[-1]
        curated_json[current_con] = {
            "electorate_size": i["electorate"]
        }
        con_result_url = "http://lda.data.parliament.uk/electionresults/" + current_con_code + ".json"
        con_details = requests.get(con_result_url).json()
        con_candidate_list = []
        for j in con_details["result"]["primaryTopic"]["candidate"]:
            candidate = {
                "name": j["fullName"]["_value"],
                "votes": j["numberOfVotes"],
                "party": j["party"]["_value"]
            }
            con_candidate_list.append(candidate)
        con_candidate_list.sort(key=extract_votes, reverse=True)
        curated_json[current_con]["candidates"] = con_candidate_list
    return curated_json


def extract_votes(candidate):
    try:
        return int(candidate["votes"])
    except KeyError:
        return 0


def generate_election_hash(election):
    sha256_hash = hashlib.sha256()
    with open("elections/" + election + ".json", "rb") as file:
        for byte_block in iter(lambda: file.read(2056), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def validate_election_file(election):
    if not isfile("elections/" + election + ".json") or not isfile("election_hashes/" + election + ".hash"):
        return False
    sha256_hash = generate_election_hash(election)
    with open("election_hashes/" + election + ".hash", "r") as hash_file:
        existing_hash = hash_file.read()
        if sha256_hash != existing_hash:
            return False
        else:
            return True

# if JSON and HASH exist, compare the two
# else, fetch the data from DDP, generate a hash and continue

def init():
    print("Running init function...")
    if not isdir("elections"):
        mkdir("elections")
        print("Created elections folder...")
    if not isdir("election_hashes"):
        mkdir("election_hashes")
        print("Created hash folder...")
    for election, code in election_codes.items():
        if not validate_election_file(election):
            print("Error with " + election + ".json, fetching details from Data.Parliament...")
            election_json = fetch_data_for_election(code)
            with open("elections/" + election + ".json", "w") as file:
                file.write(json.dumps(election_json))
                print("Computed " + election + " election")
        else:
            print(election + ".json is valid")


if __name__ == "__main__":
    # 2010 election code
    fetch_data_for_election(382386)