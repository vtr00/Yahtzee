import copy
import random
from enum import Enum
import time
import json
import logging
import logging.config
import datetime

# 定数定義
MIN_OF_PIP: int = 1
MAX_OF_PIP: int = 6
NUM_OF_DICE: int = 5

BONUS_BORDER: int = 63

POINT_BONUS: int = 35
POINT_SSTRAIGHT: int = 15
POINT_BSTRAIGHT: int = 30
POINT_YAHTZEE: int = 50

class Die:
    """サイコロ1個を表現するクラス
    """
    def __init__(self, pip: int = -1) -> None:
        """コンストラクタ

        Args:
            pip (int, optional): サイコロの値. Defaults to -1.
        """
        self.__pip__: int = -1 # サイコロの値

        if pip == -1:
            self.reroll()
        else:
            self.setPip(pip)
    
    def __str__(self) -> str:
        """文字列化関数

        Returns:
            str: 文字列
        """
        return str(self.__pip__)
    
    def __repr__(self) -> str:
        return f"{ self.__class__.__name__ }({ repr(self.__pip__) })"
    
    def pip(self) -> int:
        """サイコロの目を取得する

        Returns:
            int: サイコロの目
        """
        return self.__pip__
    
    def setPip(self, pip: int) -> None:
        """サイコロの目を設定する

        Args:
            pip (int): サイコロの目
        """
        assert 1 <= pip and pip <= MAX_OF_PIP
        self.__pip__ = pip

    def reroll(self) -> None:
        """サイコロを振り直す
        """
        self.setPip(random.randint(MIN_OF_PIP, MAX_OF_PIP))

class Dice:
    """サイコロ5個を表現する
    """
    def __init__(self, pips: list[int] = [-1, -1, -1, -1, -1]) -> None:
        """コンストラクタ

        Args:
            pips (list[int]): サイコロの目の初期値のリスト
        """
        assert NUM_OF_DICE == len(pips)

        self.__dice__: list[Die] = [Die(pip) for pip in pips] # サイコロリスト
        self.sort()

    def __iter__(self):
        return self.__dice__.__iter__()

    def __str__(self) -> str:
        return str(self.pips())

    def __repr__(self) -> str:
        return f"{ self.__class__.__name__ }({ repr((self.pips()) )})"

    def sort(self) -> None:
        """サイコロの目の昇順に並び替える
        """
        self.__dice__.sort(key=Die.pip)

    def pips(self) -> list[int]:
        """サイコロの目をリストで取得する

        Returns:
            list[int]: サイコロの目のリスト
        """
        pips: list[int] = [die.pip() for die in self.__dice__]
        return pips

    def setPips(self, pips: list[int]) -> None:
        """サイコロの目をリストで指定する

        Args:
            pips (list[int]): サイコロの目のリスト
        """
        self.__init__(pips)
        # assert NUM_OF_DICE == len(pips)

        # self.__dice__: list[Die] = [Die(pip) for pip in pips]
        # self.Sort()

    def getReroll(self, pips: list[int]) -> list[int]:
        """どのサイコロの目を振り直す必要があるかを取得する

        Args:
            pips (list[int]): 目標とするサイコロの目

        Returns:
            list[int]: 振り直し対象のリスト
        """
        lpips: list[int] = self.pips()
        lindex: int = 0
        index: int = 0
        reroll: list[int] = []
        while lindex < NUM_OF_DICE:
            if index == NUM_OF_DICE:
                reroll.append(lindex)
                lindex += 1
            elif lpips[lindex] < pips[index]:
                reroll.append(lindex)
                lindex += 1
            elif lpips[lindex] == pips[index]:
                lindex += 1
                index += 1
            else: # lpips[lindex] > pips[index]
                index += 1
        return reroll

    def reroll(self, indexes: list[int] = []) -> None:
        """指定のサイコロを振り直す

        Args:
            indexes (list[int], optional): 振り直す対象のサイコロ. Defaults to [].
        """
        if len(indexes) == 0: # 指定がなければすべて降り直し
            for die in self.__dice__:
                die.reroll()
        else:
            for index in indexes:
                assert 0 <= index and index <= len(self.__dice__) - 1
                self.__dice__[index].reroll()
        self.sort()

class Hands(Enum):
    """役"""
    Ace = 1
    Duce = 2
    Tri = 3
    Four = 4
    Five = 5
    Six = 6
    Choise = 11
    FourDice = 12
    FullHouse = 13
    SStraight = 14
    BStraight = 15
    Yahtzee = 16

class Calculator:
    """役ごとの点数を計算する
    """

    def __init__(self, logger: logging.Logger) -> None:
        """コンストラクタ

        Args:
            logger (logging.Logger): ロガー
        """
        self.__logger__: logging.Logger = logger

    def __countIf__(self, dice: Dice, num: int) -> int:
        """引数と一致する値の個数を返す

        Args:
            dice (Dice): 確認するサイコロ
            num (int): 確認する値

        Returns:
            int: 一致する値の個数
        """
        count: int = sum(pip == num for pip in dice.pips())
        return count

    def __isFourDice__(self, dice: Dice) -> bool:
        """FourDiceかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        match: int = 0
        count: int = 0
        for pip in dice.pips():
            # ダイスが一致した回数をカウント
            if match != pip:
                match = pip
                count = 1
            else:
                count += 1
            
            # 4回一致したらFourDice
            if count == 4:
                return True

        return False
    
    def __isFullHouse__(self, dice: Dice) -> bool:
        """FullHouseかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        match1: int = 0
        count1: int = 0
        match2: int = 0
        count2: int = 0

        for pip in dice.pips():
            # 2種類の値が一致した回数をカウント
            if match1 == 0:
                match1 = pip
                count1 = 1
            elif match1 == pip:
                count1 += 1
            elif match2 == 0:
                match2 = pip
                count2 = 1
            elif match2 == pip:
                count2 += 1
            else:
                return False

        # 5,0 / 2,3 / 3,2 の組み合わせならFullHouse
        if count1 == 5 or count1 * count2 == 6:
            return True

        return False
    
    def __isSStraight__(self, dice: Dice) -> bool:
        """S.Straightかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        match: int = 0
        count: int = 0

        for pip in dice.pips():
            if match == 0:
                match = pip
                count = 1
            elif match + 1 == pip:
                match += 1
                count += 1
        
        return 4 <= count
    
    def __isBStraight__(self, dice: Dice) -> bool:
        """B.Straghtかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        match: int = 0

        for pip in dice.pips():
            if match == 0:
                match = pip
            elif match + 1 == pip:
                match = pip
            else:
                return False
        return True
    
    def __isYahtzee__(self, dice: Dice) -> bool:
        """Yahtzeeかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        matches: int = 0
        for pip in dice.pips():
            # 1つでも一致しなければYahtzeeではない
            if matches == 0:
                matches = pip
            elif matches != pip:
                return False
        return True

    def calculatePoints(self, hand: Hands, dice: Dice) -> int:
        """指定された役での点数を計算する

        Args:
            hand (Hands): 役
            dice (Dice): サイコロ

        Returns:
            int: 点数
        """
        points: int = 0

        match hand:
            case Hands.Ace:
                points = self.__countIf__(dice, 1) * 1
            case Hands.Duce:
                points = self.__countIf__(dice, 2) * 2
            case Hands.Tri:
                points = self.__countIf__(dice, 3) * 3
            case Hands.Four:
                points = self.__countIf__(dice, 4) * 4
            case Hands.Five:
                points = self.__countIf__(dice, 5) * 5
            case Hands.Six:
                points = self.__countIf__(dice, 6) * 6
            case Hands.Choise:
                points = sum(dice.pips())
            case Hands.FourDice:
                points = sum(dice.pips()) if self.__isFourDice__(dice) else 0
            case Hands.FullHouse:
                points = sum(dice.pips()) if self.__isFullHouse__(dice) else 0
            case Hands.SStraight:
                points = POINT_SSTRAIGHT if self.__isSStraight__(dice) else 0
            case Hands.BStraight:
                points = POINT_BSTRAIGHT if self.__isBStraight__(dice) else 0
            case Hands.Yahtzee:
                points = POINT_YAHTZEE if self.__isYahtzee__(dice) else 0
            
        return points
    
    def getBestPoints(self, hand: Hands) -> int:
        """指定された役での最大点数を取得する

        Args:
            hand (Hands): 役

        Returns:
            int: 最大点数
        """
        points: int = 0
        match hand:
            case Hands.Ace:
                # Dice([1,1,1,1,1])
                points = 5
            case Hands.Duce:
                # Dice([2,2,2,2,2])
                points = 10
            case Hands.Tri:
                # Dice([3,3,3,3,3])
                points = 15
            case Hands.Four:
                # Dice([4,4,4,4,4])
                points = 20
            case Hands.Five:
                # Dice([5,5,5,5,5])
                points = 25
            case Hands.Six:
                # Dice([6,6,6,6,6])
                points = 30
            case Hands.Choise:
                # Dice([6,6,6,6,6])
                points = 30
            case Hands.FourDice:
                # Dice([6,6,6,6,6])
                points = 30
            case Hands.FullHouse:
                # Dice([6,6,6,6,6])
                points = 30
            case Hands.SStraight:
                points = POINT_SSTRAIGHT
            case Hands.BStraight:
                points = POINT_BSTRAIGHT
            case Hands.Yahtzee:
                points = POINT_YAHTZEE
        
        return points

class Field:
    """場
    """

    def __init__(self, logger: logging.Logger) -> None:
        """コンストラクタ

        Args:
            logger (logging.Logger): ロガー
        """

        self.__logger__: logging.Logger = logger
        # 役の計算
        self.__calculator__: Calculator = Calculator(logger)
        # 役ごとに割り当てたサイコロ
        self.__field_dice__: dict[Hands, Dice | None] = {
            Hands.Ace : None, Hands.Duce : None, Hands.Tri : None, Hands.Four : None, Hands.Five : None, Hands.Six : None, 
            Hands.Choise : None, Hands.FourDice : None, Hands.FullHouse : None, Hands.SStraight : None, Hands.BStraight : None, Hands.Yahtzee : None
        }
        # サイコロが割り当てられていない役
        self.__none_hands__: list[Hands] = [
            Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six,
            Hands.Choise, Hands.FourDice, Hands.FullHouse, Hands.SStraight, Hands.BStraight, Hands.Yahtzee
        ]
        # 役ごとの点数
        self.__field_points__: dict[Hands, int] = {
            Hands.Ace : 0, Hands.Duce : 0, Hands.Tri : 0, Hands.Four : 0, Hands.Five : 0, Hands.Six : 0, 
            Hands.Choise : 0, Hands.FourDice : 0, Hands.FullHouse : 0, Hands.SStraight : 0, Hands.BStraight : 0, Hands.Yahtzee : 0
        }
        # ボーナス点
        self.__bonus__: int = 0

    def getNoneHands(self) -> list[Hands]:
        """未割り当ての役一覧を取得する

        Returns:
            list[Hands]: 未割り当ての役
        """
        return self.__none_hands__

    def setDice(self, hand: Hands, dice: Dice, isForce: bool = False):
        """役にサイコロを割り当てる

        Args:
            hand (Hands): 役
            dice (Dice): サイコロ
            isForce (bool, optional): 既に役が割り当てられていても上書きするか. Defaults to False.
        """
        assert isForce or hand in self.__none_hands__

        self.__field_dice__[hand] = copy.deepcopy(dice)
        self.__field_points__[hand] = self.__calculator__.calculatePoints(hand, dice)
        self.__none_hands__.remove(hand)

        if self.__bonus__ == 0 and hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]:
            self.__bonus__ = POINT_BONUS if BONUS_BORDER <= self.__sumOfNumHands__() else 0

    def __sumOfNumHands__(self) -> int:
        """数字役の合計点を取得する

        Returns:
            int: 数字役の合計点
        """
        sums: int = sum([self.__field_points__[hand] for hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]])
        return sums

    def sum(self) -> int:
        """合計点を取得する

        Returns:
            int: 合計点
        """
        sums: int = sum(self.__field_points__.values())
        sums += self.__bonus__
        return sums
    
    def getInfoToSet(self, hand: Hands, dice: Dice) -> tuple[int, int, int]:
        """役にサイコロを設定したときの情報を取得する

        Args:
            hand (Hands): 役
            dice (Dice): サイコロ

        Returns:
            int: 役にサイコロを設定したときの合計点
            int: 役にサイコロを設定したときの取得点
            int: 役にサイコロを設定したときの取得点 - 役から得られる最高点(損失点)
        """
        # 現在の点
        sums: int = self.sum()

        # 設定する役の点
        handPoints: int = self.__calculator__.calculatePoints(hand, dice)
        # 設定する役の最高点
        maxHandPoints: int = self.__calculator__.getBestPoints(hand)

        # ボーナス点
        bonusPoints: int = 0
        maxBonusPoints: int = 0
        # ボーナスが未取得で、役がボーナスの対象の場合
        if self.__bonus__ == 0 and hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]:
            bonusPoints = POINT_BONUS if BONUS_BORDER <= self.__sumOfNumHands__() + handPoints else 0
            maxBonusPoints = POINT_BONUS if BONUS_BORDER <= self.__sumOfNumHands__() + maxHandPoints else 0

        # 取得点
        gainedPoints = handPoints + bonusPoints
        # 損失点
        lostPoints = gainedPoints - (maxHandPoints + maxBonusPoints)
        # 合計点
        sums += gainedPoints
        return (sums, gainedPoints, lostPoints)

    def print(self) -> None:
        """フィールドの状態をログ出力する
        """
        self.__logger__.info(f'[Field]')
        for hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]:
            value1: int = self.__field_points__[hand]
            max1: int = self.__calculator__.getBestPoints(hand)
            self.__logger__.info(f'{hand.name:<15}: {value1:>3}/{max1:>3} <- {self.__field_dice__[hand]}')

        self.__logger__.info(f'{f"(SmallSum":<15}: {self.__sumOfNumHands__():>3})')
        value2: int = self.__bonus__
        max2: int = POINT_BONUS
        self.__logger__.info(f'{f"Bonus({BONUS_BORDER}<=SS)":<15}: {value2:>3}/{max2:>3}')

        for hand in [Hands.Choise, Hands.FourDice, Hands.FullHouse, Hands.SStraight, Hands.BStraight, Hands.Yahtzee]:
            value3: int = self.__field_points__[hand]
            max3: int = self.__calculator__.getBestPoints(hand)
            self.__logger__.info(f'{hand.name:<15}: {value3:>3}/{max3:>3} <- {self.__field_dice__[hand]}')
        self.__logger__.info(f'{"Sum":<15}: {self.sum():>3}')

class HandChoiseMode(Enum):
    """役を選択するモード"""
    MaximumGain = 0 # 取得点を最大化するような役を選択する
    MinimumLost = 1 # 最適なサイコロで役を選んだ場合との差分(損失点)が最小になるような役を選択する
    Balance = 2 # 取得点を最大化しつつ損失点を最小化する役を選択する

class Evaluator:
    """場とサイコロを評価する
    """

    def __init__(self, field: Field, logger: logging.Logger) -> None:
        """コンストラクタ

        Args:
            field (Field): フィールド
            logger (logging.Logger): ロガー
        """
        # 場
        self.__field__: Field = copy.deepcopy(field)
        # ロガー
        self.__logger__: logging.Logger = logger
    
    def __bitCheck__(self, bit: int, index: int) -> bool:
        """特定のビットが立っているかを確認する

        Args:
            bit (int): 数値(2の累乗の和)
            index (int): 確認するビット

        Returns:
            bool: 確認結果
        """
        return (bit // pow(2, index)) % 2 == 1
    
    def __toIndex__(self, bit: int) -> list[int]:
        """ビットを立てる位置のリストに変換する

        Args:
            bit (int): 数値(2の累乗の和)

        Returns:
            list[int]: ビットを立てる位置のリスト
        """
        index_list: list[int] = []
        for index in range(NUM_OF_DICE):
            if self.__bitCheck__(bit, index):
                index_list.append(index)
        
        return index_list

    def __toBit__(self, indexList: list[int]) -> int:
        """2の累乗の和に変換する

        Args:
            indexList (list[int]): ビットを立てる位置のリスト

        Returns:
            int: 数値(2の累乗の和)
        """
        ret: int = sum([pow(2, index) for index in indexList])
        return ret

    def choiseHand(self, dice: Dice, mode: HandChoiseMode) -> tuple[Hands, int]:
        """役を選択する

        Args:
            dice (Dice): 現在のサイコロ
            mode (HandChoiseMode): 役選択モード

        Returns:
            Hands: 役
            int: 取得点 or 損失点(負値) or 取得点 + 損失点
        """
        # 最大取得点で選択する役
        maxGainedHand: Hands = Hands.Ace
        # 最大取得点
        maxGainedPoints: int = -100
        # 最小損失点で選択する役
        minLostHand: Hands = Hands.Ace
        # 最小損失点
        minLostPoints: int = -100
        # 最大損益点で選択する役
        maxBalanceHand: Hands = Hands.Ace
        # 最大損益点
        maxBalancePoints: int = -100

        for hand in self.__field__.getNoneHands():
            # 現在の役を設定することによる取得点、最高点との差分(損失点)を求める(ボーナスを含む)
            (_, gainedPoints, lostPoints) = self.__field__.getInfoToSet(hand, dice)
            assert 0 <= gainedPoints
            assert lostPoints <= 0

            # 取得点が大きい役を選ぶ
            if maxGainedPoints < gainedPoints:
                maxGainedHand = hand
                maxGainedPoints = gainedPoints

            # 損失点が小さい役を選ぶ
            if minLostPoints < lostPoints:
                minLostHand = hand
                minLostPoints = lostPoints
            
            # 損益点が大きい役を選ぶ
            if maxBalancePoints < gainedPoints + lostPoints:
                maxBalanceHand = hand
                maxBalancePoints = gainedPoints + lostPoints

        retHand: Hands = Hands.Ace
        retPoints: int = 0
        match mode:
            case HandChoiseMode.MaximumGain:
                retHand = maxGainedHand
                retPoints = maxGainedPoints
            case HandChoiseMode.MinimumLost:
                retHand = minLostHand
                retPoints = minLostPoints
            case HandChoiseMode.Balance:
                retHand = maxBalanceHand
                retPoints = maxBalancePoints
        
        return (retHand, retPoints)

    def evaluateReroll(self, dice: Dice, bit: int, mode: HandChoiseMode) -> tuple[float, float]:
        """振り直し時、各サイコロの出目での評価値の平均値を求める

        Args:
            dice (Dice): 振ったサイコロ
            bit (int): 振り直し対象
            mode (HandChoiseMode): 役選択モード

        Returns:
            float: 振り直し時の評価値の平均値
            float: 計算時間
        """
        sumEvaluatedPoints: int = 0 # 振り直し時の全パターンの評価値の合計
        count: int = 0 # 振り直しのパターン数
        pips: list[int] = dice.pips() # 現在の目

        startTime: float = time.time()

        # 振り直し対象なら1-6、対象外なら現在の目
        rng: list[range | list[int]] = [ range(1, MAX_OF_PIP+1) if self.__bitCheck__(bit, idx) else [pips[idx]] for idx in range(NUM_OF_DICE) ]
        for pip0 in rng[0]:
            for pip1 in rng[1]:
                for pip2 in rng[2]:
                    for pip3 in rng[3]:
                        for pip4 in rng[4]:
                            tmpPips: list[int] = [pip0, pip1, pip2, pip3, pip4]
                            tmpDice = Dice(tmpPips)
                            (_, evaluatedPoints) = self.choiseHand(tmpDice, mode)

                            sumEvaluatedPoints += evaluatedPoints
                            count += 1

        expected: float = sumEvaluatedPoints / count
        endTime: float = time.time()

        return (expected, endTime - startTime)

    def choiseReroll(self, dice: Dice, mode: HandChoiseMode) -> list[int]:
        """振り直すサイコロを選択する

        Args:
            dice (Dice): 現在のサイコロ
            mode (HandChoiseMode): 役選択モード

        Returns:
            list[int]: 振り直し対象のリスト
        """
        # 振り直し対象
        retReroll: list[int] = []
        # 最大評価値
        maxEvaluatedPoints: float = -100
        for bit in range(pow(2, NUM_OF_DICE)):
            # 振り直しを評価する
            (evaluatedPoints, time) = self.evaluateReroll(dice, bit, mode)
            # インデックスに戻す
            reroll: list[int] = self.__toIndex__(bit)
            
            self.__logger__.debug(f'{f"Expected({bit: >2})":<11}: {evaluatedPoints: >7.4f} <- {str(reroll):<16} time: {time: >7.4f}')

            # 評価値の高い振り直しを選択する
            if maxEvaluatedPoints < evaluatedPoints:
                maxEvaluatedPoints = evaluatedPoints
                retReroll = reroll

        return retReroll

#########################################################

def main() -> None:
    GAME_COUNT: int = 50
    maxSum: int = 0
    sumSum: int = 0

    with open(f'log_config.json', 'r') as f:
        log_config: dict = json.load(f)

    for gameCount in range(GAME_COUNT):
        log_config["handlers"]["fileHandler"]["filename"] = f'./logs/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        log_config["handlers"]["fileHandler2"]["filename"] = f'./logs/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}_gr.log'

        logging.config.dictConfig(log_config)
        logger: logging.Logger = logging.getLogger(__name__)
        logger_gr: logging.Logger = logging.getLogger(f"game_record")

        logger.info(f'== {gameCount:>2}/{GAME_COUNT}:')

        field = Field(logger)
        field.print()

        for choiseCount in range(len(Hands)):
            logger.info(f'=== {choiseCount+1:>2}/{len(Hands)}:')
            dice: Dice = Dice()
            evaluator: Evaluator = Evaluator(field, logger)

            # 1投目
            dice.reroll()
            logger.info(f'{"Dice1":<15}: {dice}')
            logger_gr.info(f'{dice}')

            for rollCount in [2, 3]:
                # n投目のサイコロを決める
                reroll: list[int] = evaluator.choiseReroll(dice, HandChoiseMode.MaximumGain)
                logger.info(f'{f"Reroll{rollCount}":<15}: {reroll}')
                # n投目のサイコロが存在しない場合は抜ける
                if 0 == len(reroll): break

                # n投目
                dice.reroll(reroll)
                logger.info(f'{f"Dice{rollCount}":<15}: {dice}')
                logger_gr.info(f'{dice}')

            # 役を決定する
            (hand, _) = evaluator.choiseHand(dice, HandChoiseMode.Balance)
            field.setDice(hand, dice)

            logger.info(f'{"Choise":<15}: {hand.name}')
            logger_gr.info(f'{hand.name}')
            field.print()

        if maxSum < field.sum():
            maxSum = field.sum()
        sumSum += field.sum()
    
    logger.info(f'Maximum: {maxSum}')
    logger.info(f'Average: {sumSum/GAME_COUNT}')

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