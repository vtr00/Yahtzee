import datetime
import json
import logging
import logging.config
import os
import numpy as np

import Yahtzee

# 定数定義
LOG_FOLDER_NAME: str = 'ay_logs'
GAME_COUNT: int = 100


def main() -> None:
    sumList: np.NDArray = np.array([])

    rerollMode: Yahtzee.HandChoiseMode = Yahtzee.HandChoiseMode.MaximumGain
    choiseMode: Yahtzee.HandChoiseMode = Yahtzee.HandChoiseMode.Balance

    # ロガー設定読み込み
    with open(f'log_config.json', 'r') as f:
        log_config: dict = json.load(f)

    # ログフォルダ作成
    if not os.path.exists(f'./{LOG_FOLDER_NAME}'):
        os.mkdir(f'./{LOG_FOLDER_NAME}')

    # ロガー設定
    timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_config["handlers"]["fileHandler3"]["filename"] = f'./{LOG_FOLDER_NAME}/{timestamp}_gs.log'

    for gameCount in range(1, GAME_COUNT+1):
        # ロガー設定
        log_config["handlers"]["fileHandler1"]["filename"] = f'./{LOG_FOLDER_NAME}/{timestamp}_{gameCount:03}.log'
        log_config["handlers"]["fileHandler2"]["filename"] = f'./{LOG_FOLDER_NAME}/{timestamp}_{gameCount:03}_gr.log'
        # ロガー生成
        logging.config.dictConfig(log_config)
        logger: logging.Logger = logging.getLogger(__name__)
        logger_gr: logging.Logger = logging.getLogger(f"game_record")

        logger.info(f'== {gameCount:>2}/{GAME_COUNT}:')

        field = Yahtzee.Field(logger)
        field.print()

        for choiseCount in range(len(Yahtzee.Hands)):
            logger.info(f'=== {choiseCount+1:>2}/{len(Yahtzee.Hands)}:')
            dice: Yahtzee.Dice = Yahtzee.Dice()
            evaluator: Yahtzee.Evaluator = Yahtzee.Evaluator(field, logger, rerollMode)

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
                if not reroll.exist():
                    break

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

        sumList = np.append(sumList, field.sum())

    # ロガー生成
    logger_gs: logging.Logger = logging.getLogger(f"game_statistics")

    logger_gs.info(f'Points:')
    for sum in sumList:
        logger_gs.info(f' {sum:3}')
    logger_gs.info(f'RerollMode: {rerollMode.name}')
    logger_gs.info(f'ChoiseMode: {choiseMode.name}')
    logger_gs.info(f'Maximum: {np.amax(sumList): >3.3f}')
    logger_gs.info(f'Minimum: {np.amin(sumList): >3.3f}')
    logger_gs.info(f'Average: {np.mean(sumList): >3.3f}')
    logger_gs.info(f'Median: {np.median(sumList): >3.3f}')
    logger_gs.info(f'Std.dev: {np.std(sumList): >3.3f}')


if __name__ == '__main__':
    main()
