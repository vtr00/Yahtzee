import datetime
import json
import logging
import logging.config
import os

import Yahtzee

# 定数定義
LOG_FOLDER_NAME: str = 'ay_logs'

def main() -> None:
    GAME_COUNT: int = 50
    sumList: list[int] = []

    rerollMode: Yahtzee.HandChoiseMode = Yahtzee.HandChoiseMode.MaximumGain
    choiseMode: Yahtzee.HandChoiseMode = Yahtzee.HandChoiseMode.Balance

    # ロガー設定読み込み
    with open(f'log_config.json', 'r') as f:
        log_config: dict = json.load(f)

    # ログフォルダ作成
    if not os.path.exists(f'./{LOG_FOLDER_NAME}'):
        os.mkdir(f'./{LOG_FOLDER_NAME}')

    for gameCount in range(1, GAME_COUNT+1):
        # ロガー設定
        timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_config["handlers"]["fileHandler"]["filename"] = f'./{LOG_FOLDER_NAME}/{timestamp}.log'
        log_config["handlers"]["fileHandler2"]["filename"] = f'./{LOG_FOLDER_NAME}/{timestamp}_gr.log'

        logging.config.dictConfig(log_config)
        logger: logging.Logger = logging.getLogger(__name__)
        logger_gr: logging.Logger = logging.getLogger(f"game_record")

        logger.info(f'== {gameCount:>2}/{GAME_COUNT}:')

        field = Yahtzee.Field(logger)
        field.print()

        for choiseCount in range(len(Yahtzee.Hands)):
            logger.info(f'=== {choiseCount+1:>2}/{len(Yahtzee.Hands)}:')
            dice: Yahtzee.Dice = Yahtzee.Dice()
            evaluator: Yahtzee.Evaluator = Yahtzee.Evaluator(field, logger)

            # 1投目
            dice.rollAll()
            logger.info(f'{"Dice1":<15}: {dice}')
            logger_gr.info(f'd:{dice}')

            for rollCount in [2, 3]:
                # n投目のサイコロを決める
                reroll: Yahtzee.Reroll = evaluator.choiseReroll(dice, rerollMode, choiseMode)
                logger.info(f'{f"Reroll{rollCount}":<15}: {reroll}')
                logger_gr.info(f'r:{reroll}')
                # n投目のサイコロが存在しない場合は抜ける
                if not reroll.exist(): break

                # n投目
                dice.reroll(reroll)
                logger.info(f'{f"Dice{rollCount}":<15}: {dice}')
                logger_gr.info(f'd:{dice}')

            # 役を決定する
            (hand, _) = evaluator.choiseHand(dice, choiseMode)
            field.setDice(hand, dice)

            logger.info(f'{"Choise":<15}: {hand.name}')
            logger_gr.info(f'c:{hand.name}')
            field.print()

        sumList.append(field.sum())
    
    logger.info(f'RerollMode: {rerollMode}')
    logger.info(f'ChoiseMode: {choiseMode}')
    logger.info(f'Maximum: {max(sumList)}')
    logger.info(f'Average: {sum(sumList)/len(sumList)}')

    # Max,      Max     -> Max. 264 Ave. 158.28
    # Max,      Min     -> Max. 209 Ave. 141.42
    # Max,      Balance -> Max. 267 Ave. 171.16
    # Min,      Max     -> Max. 206 Ave. 128.98
    # Min,      Min     -> Max. 238 Ave. 148.60
    # Min,      Balance -> Max. 233 Ave. 152.52
    # Balance,  Max     -> Max. 198 Ave. 131.98
    # Balance,  Min     -> Max. 206 Ave. 145.38
    # Balance,  Balance -> Max. 228 Ave. 142.76

if __name__ == '__main__':
    main()