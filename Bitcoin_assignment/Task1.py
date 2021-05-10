from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.proxy import NodeProxy
import argparse


def main():
    """
    This script creates a P2SH address containing a OP_CHECKLOCKTIMEVERIFY plus
    a P2PKH locking funds with a key as well as for asked blocks/ time
    :return:
    """
    # setup regtest network
    setup('regtest')
    priv = PrivateKey('')
    parser = argparse.ArgumentParser(description='Bitcoin Script for Task I')
    parser.add_argument('--public_key', type=int, help='Insert a public key')
    parser.add_argument('--time_loc',
                        help='Insert a parameter (block height/Unix Epoch time that funds should be locked')

    args = parser.parse_args()
    public_key = args.public_key
    absolute_param = args.time_loc

    # Ask for public key /P2SH address



    # set values
    relative_blocks = 20

    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, relative_blocks)

    # secret key corresponding to the pubkey needed for the P2SH (P2PKH) transaction
    p2pkh_sk = PrivateKey('cRvyLwCPLU88jsyj94L7iJjQX5C2f8koG4G2gevN4BeSGcEvfKe9')

    # get the address (from the public key)
    p2pkh_addr = p2pkh_sk.get_public_key().get_address()

    # create the redeem script
    redeem_script = Script(
        [seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(),
         'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # create a P2SH address from a redeem script
    addr = P2shAddress.from_script(redeem_script)
    print(addr.to_string())


if __name__ == "__main__":
    main()
