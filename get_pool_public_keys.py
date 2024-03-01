from solana.rpc.async_api import AsyncClient

from solders.pubkey import Pubkey

import time
from solana.rpc.commitment import Commitment

from utils.layouts import AMM_INFO_LAYOUT_V4_1
from utils.layouts import MARKET_LAYOUT
from utils.constants import RAY_AUTHORITY_V4, RAY_V4

# RPC_HTTPS_URL = "https://mainnet.helius-rpc.com/?api-key=aaaa-111-sss-cccc-dddd"



async def gen_pool(amm_id, ctx):


    try:
        amm_id = Pubkey.from_string(amm_id)
        # ctx = AsyncClient(RPC_HTTPS_URL, commitment="confirmed")

        start = time.time()
        while True:
            try:
                amm_data = (await ctx.get_account_info_json_parsed(amm_id)).value.data
                break
            except:
                if (time.time() - start) > 3:
                    return {"error" : "server timeout - took too long to find the pool info"}  
                pass

        amm_data_decoded = AMM_INFO_LAYOUT_V4_1.parse(amm_data)
        OPEN_BOOK_PROGRAM = Pubkey.from_bytes(amm_data_decoded.serumProgramId)
        marketId = Pubkey.from_bytes(amm_data_decoded.serumMarket)
        # print("Market --- ", marketId))
        try:
            while True:
                try:
                    marketInfo = (
                        await ctx.get_account_info_json_parsed(marketId)
                    ).value.data
                    break
                except:
                    if (time.time() - start) > 3:
                        return {"error" : "server timeout - took too long to find the pool info"} 
                    pass

            market_decoded = MARKET_LAYOUT.parse(marketInfo)


            pool_keys = {
                "amm_id": amm_id,
                "base_mint": Pubkey.from_bytes(market_decoded.base_mint),
                "quote_mint": Pubkey.from_bytes(market_decoded.quote_mint),
                "lp_mint": Pubkey.from_bytes(amm_data_decoded.lpMintAddress),
                "version": 4,

                "base_decimals": amm_data_decoded.coinDecimals,
                "quote_decimals": amm_data_decoded.pcDecimals,
                "lpDecimals": amm_data_decoded.coinDecimals,
                "programId": RAY_V4,
                "authority": RAY_AUTHORITY_V4,

                "open_orders": Pubkey.from_bytes(amm_data_decoded.ammOpenOrders),

                "target_orders": Pubkey.from_bytes(amm_data_decoded.ammTargetOrders),


                "base_vault": Pubkey.from_bytes(amm_data_decoded.poolCoinTokenAccount),
                "quote_vault": Pubkey.from_bytes(amm_data_decoded.poolPcTokenAccount),

                "withdrawQueue": Pubkey.from_bytes(amm_data_decoded.poolWithdrawQueue),
                "lpVault": Pubkey.from_bytes(amm_data_decoded.poolTempLpTokenAccount),

                "marketProgramId": OPEN_BOOK_PROGRAM,
                "market_id": marketId,

                "market_authority": Pubkey.create_program_address(
                    [bytes(marketId)]
                    + [bytes([market_decoded.vault_signer_nonce])]
                    + [bytes(7)],
                    OPEN_BOOK_PROGRAM,
                ),

                "market_base_vault": Pubkey.from_bytes(market_decoded.base_vault),
                "market_quote_vault": Pubkey.from_bytes(market_decoded.quote_vault),
                "bids": Pubkey.from_bytes(market_decoded.bids),
                "asks": Pubkey.from_bytes(market_decoded.asks),
                "event_queue": Pubkey.from_bytes(market_decoded.event_queue),
                "pool_open_time": amm_data_decoded.poolOpenTime
            }


            return pool_keys
        except:
            {"error" : "unexpected error occured"}
    except:
        return {"error" : "incorrect pair address"}