from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from get_pool_strings import gen_pool as gen_pool_strings
from get_pool_public_keys import gen_pool as gen_pool_public_keys
import asyncio

RPC_HTTPS_URL = "https://mainnet.helius-rpc.com/?api-key=aaaa-111-sss-cccc-dddd"




async def test():
    amm_id = "DoXRUh3NEd2bXK4X5V4hLDKqvWXXLej2ifs5stpX8eNN" #test

    ctx = AsyncClient(RPC_HTTPS_URL, commitment=Confirmed)


    keys_in_the_form_strings = await gen_pool_strings(amm_id,ctx)
    print(keys_in_the_form_strings)
    
    print("*"*500)



    keys_in_the_form_of_public_keys = await  gen_pool_public_keys(amm_id,ctx)
    print(keys_in_the_form_of_public_keys)


asyncio.run(test())