#!/usr/bin/env python3
# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

'''
	Farming bot for Dofus game
'''

import os
import platform
from gui.main import BotWindow

def main():
    bot = BotWindow()
    bot.log('Bot window loaded')

    if platform.system() == "Windows":
        bot.log("Detected Windows operating system.")
        # Add any necessary Windows-specific initialization here

    bot.main()

if __name__ == "__main__":
    main()

