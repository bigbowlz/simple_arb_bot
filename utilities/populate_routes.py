from web3 import Web3
import json
import requests
import os
import argparse
from dotenv import load_dotenv
from utilities.balances import(get_token_decimals)
'''
populate_routes.py

Populates routes in mainnet.json by permutating the combination of routers and tokens, 
and checking if there's a viable trade route on-chain.

Command-line arguments:
  -h, --help  show this help message and exit
  --ABI       Populate ABI files for the router contracts in mainnet.json.
  --route     Populate viable trade routes for two tokens on two dexes in mainnet.json.

Author: ILnaw
Version: 0.0.1
'''
def setup():
# Connect to a mainnet node.
    node_url = "http://127.0.0.1:8545"
    web3 = Web3(Web3.HTTPProvider(node_url))

    if not web3.is_connected():
        raise Exception("Unable to connect to localhost")
    else:
        print("Connected to localhost")
        
    #Convert JSON file into a Python dictionary
    with open("configs/mainnet.json", "r") as file:
        data = json.load(file)
        print("Data read from json file.")
    
    # Load environment variables from .env file
    env_path = '.env' 
    load_dotenv(env_path)

    # Etherscan API URL and your API key from the environment variables
    api_url = "https://api.etherscan.io/api"
    api_key = os.getenv("ETHERSCAN_API_KEY")

    return web3, data, api_key, api_url

def checksum(web3, data):
    '''
    Converts contract addresses to the correct checksum format.
    '''
    for router in data["routers"]:
        router_address = router["address"]
        router["address"] = web3.to_checksum_address(router_address)
    print("All router addresses updated to checksum addresses.")

    for baseAsset in data["baseAssets"]:
        baseAsset_address = baseAsset["address"]
        baseAsset["address"] = web3.to_checksum_address(baseAsset_address)
    print("All baseAsset addresses updated to checksum addresses.")

    for token in data["tokens"]:
        token_address = token["address"]
        token["address"] = web3.to_checksum_address(token_address)
    print("All token addresses updated to checksum addresses.")

def populate_ABIs(data, api_key, api_url):
    '''
    Populates ABI files for the router contracts in mainnet.json, 
    and store ABI files in the configs/router_AIBs directory.

    Param:
    data: Python dictionary format of the network config JSON file.
    '''
    for router in data["routers"]:
        create_contract_ABI(router, api_key, api_url)
    
def create_contract_ABI(dex_contract, api_key, api_url):
    '''
    Writes ABI of the contract to a JSON file to store in the configs/router_AIBs directory.
    
    Param:
    dex_contract (dict): consists of the key "dex" of a string value, and the key "address" of a string value. 
    api_key: API key to a block explorer.
    api_url: API url to a block explorer.
    '''
    #API parameters
    params = {
        "module": "contract",
        "action": "getabi",
        "address": dex_contract["address"],
        "apikey": api_key
    }

    # Fetch the contract ABI
    response = requests.get(api_url, params=params)
    abi = response.json().get("result")

    if abi:
    # Save the ABI to a JSON file
        with open('configs/router_ABIs/' + dex_contract["dex"] + '_abi.json', 'w') as abi_file:
            json.dump(json.loads(abi), abi_file, indent=4)
        print("ABI saved to " + 'configs/router_ABIs/' + dex_contract["dex"] + '_abi.json')
    else:
        print("Failed to fetch ABI")

def populate_routes(data, web3):
    '''
    Populates routes in mainnet.json by permutating the combination of routers and tokens, 
    and checking if there's a viable trade route on-chain.

    Param:
    data: Python dictionary format of the network config JSON file.
    '''
    # Remove all existing routes
    data["routes"] = []

    # Permutate routers and tokens
    for i in range(len(data["routers"])-1):
        for j in range(i+1, len(data["routers"])):
            for m in range(len(data["tokens"])-1):
                for n in range(m+1, len(data["tokens"])):
                    router1_name = data["routers"][i]["dex"]
                    router1_address = data["routers"][i]["address"]
                    router2_name = data["routers"][j]["dex"]
                    router2_address = data["routers"][j]["address"]
                    token1_address = data["tokens"][m]["address"]
                    token2_address = data["tokens"][n]["address"]

                    # if route is valid, add route to the json file
                    if check_route(router1_name, router1_address, router2_name, router2_address, token1_address, token2_address, web3):
                        route = {}
                        route["router1"] = router1_address
                        route["router2"] = router2_address
                        route["token1"] = token1_address
                        route["token2"] = token2_address
                        data["routes"].append(route)
    
    # Write the updated data back to the JSON file
    with open("configs/mainnet.json", "w") as file:
        json.dump(data, file, indent=4)
        print("All possible routes checked and written to json.")
                            

def check_route(router1_name, router1_address, router2_name, router2_address, token1_address, token2_address, web3):
    '''
    Checks if a route is valid.

    Params:
    router1_name: the string value of the name of router1.
    router1_address: the string value of the address of the router1 contract.
    router2_name: the string value of the name of router2.
    router2_address: the string value of the address of the router2 contract.
    token1_address: the string value of the address of the token1 contract.
    token2_address: the string value of the address of the token2 contract.
    web3: an instance of the Web3 class from the web3.py library.
    '''

    # Load router1 and router2 ABI
    with open('configs/router_ABIs/' + router1_name + '_abi.json', 'r') as router1_abi_file:
        router1_abi = json.load(router1_abi_file)
    with open('configs/router_ABIs/' + router2_name + '_abi.json', 'r') as router2_abi_file:
        router2_abi = json.load(router2_abi_file)

    # Create contract instances for the routers
    router1 = web3.eth.contract(address=router1_address, abi=router1_abi)
    router2 = web3.eth.contract(address=router2_address, abi=router2_abi)

    # Check if the route is valid on both routers
    is_valid_on_router1 = is_valid_pair(router1, token1_address, token2_address, web3)
    is_valid_on_router2 = is_valid_pair(router2, token1_address, token2_address, web3)

    if is_valid_on_router1 and is_valid_on_router2:
        print(f"Route valid on {router1_name} and {router2_name}")
        print(f"..for {token1_address} and {token2_address}")
        return True
    return False

def is_valid_pair(router, token1, token2, web3):
    '''
    Checks if a token pair is valid on a given router.

    Params:
    router: web3.py contract instance for a router
    token1: address of token1 
    token2: address of token2
    '''
    try:
        token1_decimals = get_token_decimals(token1, web3)
        if token1_decimals is None:
            return False
        
        amount_in = 100 ** token1_decimals  # Try to trade with 10 amount of token1
        amounts_out = router.functions.getAmountsOut(amount_in, [token1, token2]).call()
        return amounts_out is not None and len(amounts_out) > 1
    except Exception as e:
        print(f"Invalid pair {token1}->{token2}")
        return False

if __name__ == "__main__":
    web3, data, api_key, api_url = setup()

    # create the command-line parser
    parser = argparse.ArgumentParser(description="Completed arbitrage config setup process, parsing arguments...")

    # add arguments
    parser.add_argument('--ABI', action='store_true', help='Populate ABI files for the router contracts in mainnet.json.')
    parser.add_argument('--route', action='store_true', help='Populate viable trade routes for two tokens on two dexes in mainnet.json.')
    parser.add_argument('--checksum', action='store_true', help='Convert addresses in mainnet.json to checksum format.')

    # parse the arguments
    args = parser.parse_args()

    # access the arguments
    if args.ABI:
        populate_ABIs(data, api_key, api_url)
    if args.route:
        populate_routes(data, web3)
    if args.checksum:
        checksum(web3, data)
        # Write the updated data back to the JSON file
        with open("configs/mainnet.json", "w") as file:
            json.dump(data, file, indent=4)
            print("Updated routes and addresses written to json file.")

