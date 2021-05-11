from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2shAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script
from bitcoinutils.proxy import NodeProxy
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
# rpcuser=Alice
# rpcpassword=DONT_USE_THIS_YOU_WILL_GET_ROBBED_8ak1gI25KFTvjovL3gAM967mies3E=
import argparse
from decimal import Decimal


def main():
    # setup regtest network
    setup('regtest')
    proxy = NodeProxy('alice', 'DONT_USE_THIS_YOU_WILL_GET_ROBBED_8ak1gI25KFTvjovL3gAM967mies3E=').get_proxy()
    print(proxy.getblockcount())
    parser = argparse.ArgumentParser(description='Bitcoin Script for Task I')
    parser.add_argument('-private_key', help='Insert a public key')
    parser.add_argument('--time_loc', type=int,
                        help='Insert a parameter (block height/Unix Epoch time that funds should be locked')
    parser.add_argument('-p2sh', help='Insert a p2sh')
    parser.add_argument('-p2pkh', help='Insert a p2pkh')

    # the key that corresponds to the P2WPKH address
    # priv = PrivateKey('cNho8fw3bPfLKT4jPzpANTsxTsP8aTdVBD6cXksBEXt4KhBN7uVk')
    args = parser.parse_args()
    priv = args.private_key
    p2sh = args.time_loc
    p2pkh = args.p2pkh

    pub = priv.get_public_key()

    proxy.list_unspent(p2sh)
    # the p2sh script and the corresponding address
    redeem_script = pub.get_segwit_address().to_script_pub_key()
    p2sh_addr = P2shAddress.from_script(redeem_script)

    # the UTXO of the P2SH-P2WPKH that we are trying to spend
    inp = TxInput('95c5cac558a8b47436a3306ba300c8d7af4cd1d1523d35da3874153c66d99b09', 0)

    # exact amount of UTXO we try to spent
    amount = 0.0014

    # the address to send funds to
    to_addr = P2pkhAddress('mvBGdiYC8jLumpJ142ghePYuY8kecQgeqS')

    # the output sending 0.001 -- 0.0004 goes to miners as fee -- no change
    out = TxOutput(to_satoshis(0.001), to_addr.to_script_pub_key())

    # create a tx with at least one segwit input
    tx = Transaction([inp], [out], has_segwit=True)

    # script code is the script that is evaluated for a witness program type; each
    # witness program type has a specific template for the script code
    # script code that corresponds to P2WPKH (it is the classic P2PKH)
    script_code = pub.get_address().to_script_pub_key()

    # calculate signature using the appropriate script code
    # remember to include the original amount of the UTXO
    sig = priv.sign_segwit_input(tx, 0, script_code, to_satoshis(amount))

    # script_sig is the redeem script passed as a single element
    inp.script_sig = Script([redeem_script.to_hex()])

    # finally, the unlocking script is added as a witness
    tx.witnesses.append(Script([sig, pub.to_hex()]))

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + tx.serialize())


if __name__ == "__main__":
    main()