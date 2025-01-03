import copy
import logging
import logging.config
import random
import time
from enum import Enum
from typing import Iterator

# 定数定義
MIN_OF_PIP: int = 1  # サイコロの出目の最小値
MAX_OF_PIP: int = 6  # サイコロの出目の最大値
NUM_OF_DICE: int = 5  # サイコロの個数

BONUS_BORDER: int = 63  # ボーナス点が入る基準

POINT_BONUS: int = 35  # ボーナス点
POINT_SSTRAIGHT: int = 15  # S.Straightの点数
POINT_BSTRAIGHT: int = 30  # B.Straightの点数
POINT_YAHTZEE: int = 50  # Yahtzeeの点数


class Die:
    """サイコロ1個を表現するクラス
    """

    def __init__(self, pip: int = -1) -> None:
        """コンストラクタ

        Args:
            pip (int, optional): サイコロの値. Defaults to -1.
        """
        self.__pip__: int = -1  # サイコロの値

        if pip == -1:
            self.roll()
        else:
            self.setPip(pip)

    def __str__(self) -> str:
        """文字列化する

        Returns:
            str: 文字列
        """
        return str(self.__pip__)

    def __repr__(self) -> str:
        """文字列表現化する

        Returns:
            str: 文字列
        """
        return f"{ self.__class__.__name__ }({ repr(self.__pip__) })"

    def __eq__(self, other) -> bool:
        """equal operator

        Args:
            other (Any): 比較対象

        Returns:
            bool: 比較結果
        """
        if type(other) == Die:
            return self.__pip__ == other.__pip__
        assert False

    def __ne__(self, other) -> bool:
        """not equal operator

        Args:
            other (Any): 比較対象

        Returns:
            bool: 比較結果
        """
        return not self.__eq__(other)

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

    def roll(self) -> None:
        """サイコロを振る
        """
        self.setPip(random.randint(MIN_OF_PIP, MAX_OF_PIP))


class Reroll:
    def __init__(self, reroll: list[int] | int = []) -> None:
        """コンストラクタ

        Args:
            reroll (list[int] | int, optional): 振り直し対象のリストまたは数値. Defaults to [].
        """
        self.__indexList__: list[int] = []
        if type(reroll) is list[int]:
            assert 0 <= min(reroll) and max(reroll) < NUM_OF_DICE
            assert len(reroll) == len(set(reroll))
            self.__indexList__: list[int] = reroll.sort()
        elif type(reroll) is int:
            assert 0 <= reroll and reroll < pow(2, 5)
            self.__indexList__: list[int] = self.__toIndexList__(reroll)

    @classmethod
    def __bitCheck__(cls, bit: int, index: int) -> bool:
        """特定のビットが立っているかを確認する

        Args:
            bit (int): 数値(2の累乗の和)
            index (int): 確認するビット

        Returns:
            bool: 確認結果
        """
        return (bit // pow(2, index)) % 2 == 1

    @classmethod
    def __toIndexList__(cls, bit: int) -> list[int]:
        """ビットを立てる位置のリストに変換する

        Args:
            bit (int): 数値(2の累乗の和)

        Returns:
            list[int]: ビットを立てる位置のリスト
        """
        index_list: list[int] = []
        for index in range(NUM_OF_DICE):
            if cls.__bitCheck__(bit, index):
                index_list.append(index)

        return index_list

    @classmethod
    def __toBit__(cls, indexList: list[int]) -> int:
        """2の累乗の和に変換する

        Args:
            indexList (list[int]): ビットを立てる位置のリスト

        Returns:
            int: 数値(2の累乗の和)
        """
        ret: int = sum([pow(2, index) for index in indexList])
        return ret

    def __str__(self) -> str:
        """文字列化する

        Returns:
            str: 文字列
        """
        retList: list[str] = []
        for index in range(NUM_OF_DICE):
            if index in self.__indexList__:
                retList += [f'{index+1}']
            else:
                retList += ['-']

        return f'[{", ".join(retList)}]'

    def __repr__(self) -> str:
        """文字列表現化する

        Returns:
            str: 文字列
        """
        return f'{ self.__class__.__name__ }({repr(self.__indexList__)})'

    def exist(self) -> bool:
        """振り直し対象が存在するか

        Returns:
            bool: 確認結果
        """
        return len(self.__indexList__) != 0

    def bitCheck(self, index: int) -> bool:
        """特定のビットが立っているかを確認する

        Args:
            index (int): 確認するビット

        Returns:
            bool: 確認結果
        """
        return self.__bitCheck__(self.__toBit__(self.__indexList__), index)

    def toList(self) -> list[int]:
        """リストに変換する

        Returns:
            list[int]: 振り直し対象のインデックスのリスト
        """
        return self.__indexList__


class Dice:
    """サイコロ5個を表現する
    """

    def __init__(self, pips: list[int] = [-1, -1, -1, -1, -1]) -> None:
        """コンストラクタ

        Args:
            pips (list[int]): サイコロの目の初期値のリスト
        """
        assert NUM_OF_DICE == len(pips)

        self.__dice__: list[Die] = [Die(pip) for pip in pips]  # サイコロリスト
        self.sort()

    def __iter__(self) -> Iterator[Die]:
        """イテレータを取得する

        Returns:
            Iterator[Die]: イテレータ
        """
        return self.__dice__.__iter__()

    def __str__(self) -> str:
        """文字列化する

        Returns:
            str: 文字列
        """
        return str(self.pips())

    def __repr__(self) -> str:
        """文字列表現化する

        Returns:
            str: 文字列
        """
        return f'{ self.__class__.__name__ }({ repr((self.pips()) )})'

    def __eq__(self, other) -> bool:
        """equal operator

        Args:
            other (Any): 比較対象

        Returns:
            bool: 比較結果
        """
        if type(other) == Dice:
            return self.__dice__ == other.__dice__
        assert False

    def __ne__(self, other) -> bool:
        """not equal operator

        Args:
            other (Any): 比較対象

        Returns:
            bool: 比較結果
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(str(self))

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
            else:  # lpips[lindex] > pips[index]
                index += 1
        return reroll

    def rollAll(self) -> None:
        """すべてのサイコロを振る
        """
        for die in self.__dice__:
            die.roll()
        self.sort()

    def reroll(self, reroll: Reroll) -> None:
        """指定のサイコロを振り直す

        Args:
            reroll (Reroll): 振り直し対象
        """
        indexes: list[int] = reroll.toList()
        for index in indexes:
            assert 0 <= index and index <= len(self.__dice__) - 1
            self.__dice__[index].roll()
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

    def __init__(self) -> None:
        """コンストラクタ
        """
        pass

    @classmethod
    def __countIf__(cls, dice: Dice, num: int) -> int:
        """引数と一致する値の個数を返す

        Args:
            dice (Dice): 確認するサイコロ
            num (int): 確認する値

        Returns:
            int: 一致する値の個数
        """
        count: int = sum(pip == num for pip in dice.pips())
        return count

    @classmethod
    def __isFourDice__(cls, dice: Dice) -> bool:
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

    @classmethod
    def __isFullHouse__(cls, dice: Dice) -> bool:
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

    @classmethod
    def __isSStraight__(cls, dice: Dice) -> bool:
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

    @classmethod
    def __isBStraight__(cls, dice: Dice) -> bool:
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

    @classmethod
    def __isYahtzee__(cls, dice: Dice) -> bool:
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

    @classmethod
    def GetNumHands(cls) -> list[Hands]:
        """数字役を返す

        Returns:
            list[Hands]: 数字役
        """
        return [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]

    @classmethod
    def calculatePoints(cls, hand: Hands, dice: Dice) -> int:
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
                points = cls.__countIf__(dice, 1) * 1
            case Hands.Duce:
                points = cls.__countIf__(dice, 2) * 2
            case Hands.Tri:
                points = cls.__countIf__(dice, 3) * 3
            case Hands.Four:
                points = cls.__countIf__(dice, 4) * 4
            case Hands.Five:
                points = cls.__countIf__(dice, 5) * 5
            case Hands.Six:
                points = cls.__countIf__(dice, 6) * 6
            case Hands.Choise:
                points = sum(dice.pips())
            case Hands.FourDice:
                points = sum(dice.pips()) if cls.__isFourDice__(dice) else 0
            case Hands.FullHouse:
                points = sum(dice.pips()) if cls.__isFullHouse__(dice) else 0
            case Hands.SStraight:
                points = POINT_SSTRAIGHT if cls.__isSStraight__(dice) else 0
            case Hands.BStraight:
                points = POINT_BSTRAIGHT if cls.__isBStraight__(dice) else 0
            case Hands.Yahtzee:
                points = POINT_YAHTZEE if cls.__isYahtzee__(dice) else 0

        return points

    @classmethod
    def getBestPoints(cls, hand: Hands) -> int:
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
        # 役ごとに割り当てたサイコロ
        self.__field_dice__: dict[Hands, Dice | None] = {
            Hands.Ace: None, Hands.Duce: None, Hands.Tri: None, Hands.Four: None, Hands.Five: None, Hands.Six: None,
            Hands.Choise: None, Hands.FourDice: None, Hands.FullHouse: None, Hands.SStraight: None, Hands.BStraight: None, Hands.Yahtzee: None
        }
        # サイコロが割り当てられていない役
        self.__none_hands__: list[Hands] = [
            Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six,
            Hands.Choise, Hands.FourDice, Hands.FullHouse, Hands.SStraight, Hands.BStraight, Hands.Yahtzee
        ]
        # 役ごとの点数
        self.__field_points__: dict[Hands, int] = {
            Hands.Ace: 0, Hands.Duce: 0, Hands.Tri: 0, Hands.Four: 0, Hands.Five: 0, Hands.Six: 0,
            Hands.Choise: 0, Hands.FourDice: 0, Hands.FullHouse: 0, Hands.SStraight: 0, Hands.BStraight: 0, Hands.Yahtzee: 0
        }
        # ボーナス点
        self.__bonus__: int = 0

    def getNoneHands(self) -> list[Hands]:
        """未割り当ての役一覧を取得する

        Returns:
            list[Hands]: 未割り当ての役
        """
        return self.__none_hands__

    def setDice(self, hand: Hands, dice: Dice, isForce: bool = False) -> None:
        """役にサイコロを割り当てる

        Args:
            hand (Hands): 役
            dice (Dice): サイコロ
            isForce (bool, optional): 既に役が割り当てられていても上書きするか. Defaults to False.
        """
        assert isForce or hand in self.__none_hands__

        self.__field_dice__[hand] = copy.deepcopy(dice)
        self.__field_points__[hand] = Calculator.calculatePoints(hand, dice)
        self.__none_hands__.remove(hand)

        if self.__bonus__ == 0 and hand in Calculator.GetNumHands():
            self.__bonus__ = POINT_BONUS if BONUS_BORDER <= self.__sumOfNumHands__() else 0

    def __sumOfNumHands__(self) -> int:
        """数字役の合計点を取得する

        Returns:
            int: 数字役の合計点
        """
        sums: int = sum([self.__field_points__[hand] for hand in Calculator.GetNumHands()])
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
        handPoints: int = Calculator.calculatePoints(hand, dice)
        # 設定する役の最高点
        maxHandPoints: int = Calculator.getBestPoints(hand)

        # ボーナス点
        bonusPoints: int = 0
        maxBonusPoints: int = 0
        # ボーナスが未取得で、役がボーナスの対象の場合
        if self.__bonus__ == 0 and hand in Calculator.GetNumHands():
            # その役を選択することで得られるボーナス点を計算する
            bonusPoints = POINT_BONUS if BONUS_BORDER <= self.__sumOfNumHands__() + handPoints else 0
            # 最大点でその役を選択することで得られるボーナス点を計算する
            maxBonusPoints = POINT_BONUS if BONUS_BORDER <= self.__sumOfNumHands__() + maxHandPoints else 0
            # TODO: その役を選択したことでボーナス点を得られなくなった場合に損失として扱う

        # 取得点
        gainedPoints = handPoints + bonusPoints
        # 損失点
        lostPoints = gainedPoints - (maxHandPoints + maxBonusPoints)

        assert 0 <= gainedPoints
        assert lostPoints <= 0

        # 合計点
        sums += gainedPoints
        return (sums, gainedPoints, lostPoints)

    def print(self) -> None:
        """フィールドの状態をログ出力する
        """
        self.__logger__.info(f'[Field]')
        for hand in Calculator.GetNumHands():
            value1: int = self.__field_points__[hand]
            max1: int = Calculator.getBestPoints(hand)
            self.__logger__.info(f'{hand.name:<15}: {value1:>3}/{max1:>3} <- {self.__field_dice__[hand]}')

        self.__logger__.info(f'{f"(SmallSum":<15}: {self.__sumOfNumHands__():>3})')
        value2: int = self.__bonus__
        max2: int = POINT_BONUS
        self.__logger__.info(f'{f"Bonus({BONUS_BORDER}<=SS)":<15}: {value2:>3}/{max2:>3}')

        for hand in [Hands.Choise, Hands.FourDice, Hands.FullHouse, Hands.SStraight, Hands.BStraight, Hands.Yahtzee]:
            value3: int = self.__field_points__[hand]
            max3: int = Calculator.getBestPoints(hand)
            self.__logger__.info(f'{hand.name:<15}: {value3:>3}/{max3:>3} <- {self.__field_dice__[hand]}')
        self.__logger__.info(f'{"Sum":<15}: {self.sum():>3}')


class HandChoiseMode(Enum):
    """役を選択するモード"""
    MaximumGain = 0  # 取得点を最大化するような役を選択する
    MinimumLost = 1  # 最適なサイコロで役を選んだ場合との差分(損失点)が最小になるような役を選択する
    Balance = 2  # 取得点を最大化しつつ損失点を最小化する役を選択する


class Evaluator:
    """場とサイコロを評価する
    """

    def __init__(self, field: Field, logger: logging.Logger, defaultMode: HandChoiseMode) -> None:
        """コンストラクタ

        Args:
            field (Field): フィールド
            logger (logging.Logger): ロガー
            defaultMode (HandChoiseMode): デフォルトモード
        """
        # 場
        self.__field__: Field = copy.deepcopy(field)
        # ロガー
        self.__logger__: logging.Logger = logger
        # デフォルト役選択モード
        self.__defaultMode__: HandChoiseMode = defaultMode
        # デフォルト役選択モード時の評価結果
        self.__diceToTupleDict__: dict[Dice, tuple[Hands, int]] = {}

    def choiseHand(self, dice: Dice, modeAtHandChoise: HandChoiseMode, modeAtReturnPoint: HandChoiseMode | None = None) -> tuple[Hands, int]:
        """役を選択する

        Args:
            dice (Dice): 現在のサイコロ
            modeAtHandChoise (HandChoiseMode): 選択モード(役選択時)
            modeAtReturnPoint (HandChoiseMode): 選択モード(戻り値). Defaults to same of modeAtHandChoise.

        Returns:
            Hands: 選択モード(役選択時)に応じた役
            int: 選択モード(戻り値)に応じた値(取得点 or 損失点(負値) or 取得点 + 損失点)
        """
        if modeAtReturnPoint is None:
            modeAtReturnPoint = modeAtHandChoise

        # 選択する役
        retHand: Hands = Hands.Ace
        # 返す値
        retPoints: int = 0

        # 最大点
        maxPoints: int = -100

        for hand in self.__field__.getNoneHands():
            # 現在の役を設定することによる取得点、最高点との差分(損失点)を求める(ボーナスを含む)
            (_, gainedPoints, lostPoints) = self.__field__.getInfoToSet(hand, dice)

            # 比較対象を選択する
            comparedPoints: int = 0
            match modeAtHandChoise:
                case HandChoiseMode.MaximumGain:
                    # 取得点で比較する
                    comparedPoints = gainedPoints
                case HandChoiseMode.MinimumLost:
                    # 損失点で比較する
                    comparedPoints = lostPoints
                case HandChoiseMode.Balance:
                    # 損益点で比較する
                    comparedPoints = gainedPoints + lostPoints

            # 比較対象が大きいとき、手を選択する
            if maxPoints < comparedPoints:
                retHand = hand
                maxPoints = comparedPoints

                # 手を選択したときの点を取得する
                match modeAtReturnPoint:
                    case HandChoiseMode.MaximumGain:
                        retPoints = gainedPoints
                    case HandChoiseMode.MinimumLost:
                        retPoints = lostPoints
                    case HandChoiseMode.Balance:
                        retPoints = gainedPoints + lostPoints
            elif maxPoints == comparedPoints:
                pass  # TODO: どの役を選ぶのが適切か

        return (retHand, retPoints)

    def evaluateReroll(self, dice: Dice, reroll: Reroll, mode: HandChoiseMode, modeBySelf: HandChoiseMode) -> tuple[float, float]:
        """振り直し時、各サイコロの出目での評価値の平均値を求める

        Args:
            dice (Dice): 振ったサイコロ
            reroll (Reroll): 振り直し対象
            mode (HandChoiseMode): 役選択/評価モード
            modeBySelf (HandChoiseMode): 役選択モード(振り直しなし時)

        Returns:
            float: 振り直し時の評価値の平均値
            float: 計算時間
        """
        evaluatedPointsList: list[int] = []  # 振り直し時の全パターンの評価値リスト

        maxEvaluatedDice: Dice = dice  # 最大評価値でのサイコロ
        maxEvaluatedHand: Hands = Hands.Ace  # 最大評価値での手
        maxEvaluatedPoints: int = -100  # 最大評価値での評価値

        startTime: float = time.time()

        pips: list[int] = dice.pips()  # 現在の目
        # 振り直し対象なら1-6、対象外なら現在の目
        rng: list[range | list[int]] = [range(1, MAX_OF_PIP+1) if reroll.bitCheck(idx) else [pips[idx]] for idx in range(NUM_OF_DICE)]
        for pip0 in rng[0]:
            for pip1 in rng[1]:
                for pip2 in rng[2]:
                    for pip3 in rng[3]:
                        for pip4 in rng[4]:
                            tmpPips: list[int] = [pip0, pip1, pip2, pip3, pip4]
                            tmpDice = Dice(tmpPips)
                            if dice == tmpDice:  # 振り直しなしの場合
                                (tmpHand, evaluatedPoints) = self.choiseHand(tmpDice, modeBySelf, mode)
                            elif self.__defaultMode__ == mode:  # 計算済のモードの場合
                                if tmpDice in self.__diceToTupleDict__:  # 計算済の場合
                                    (tmpHand, evaluatedPoints) = self.__diceToTupleDict__[tmpDice]
                                else:  # 未計算の場合
                                    (tmpHand, evaluatedPoints) = self.choiseHand(tmpDice, mode)
                                    self.__diceToTupleDict__[tmpDice] = (tmpHand, evaluatedPoints)
                            else:
                                (tmpHand, evaluatedPoints) = self.choiseHand(tmpDice, mode)

                            # self.__logger__.debug(f'{f"Evaluated({tmpDice})":<11}: {evaluatedPoints: >3} <- {tmpHand:<16}')

                            # ログ出力用に最大評価時のサイコロ、手、最大評価値を保存する
                            if maxEvaluatedPoints < evaluatedPoints:
                                maxEvaluatedDice = tmpDice
                                maxEvaluatedHand = tmpHand
                                maxEvaluatedPoints = evaluatedPoints

                            evaluatedPointsList.append(evaluatedPoints)

        self.__logger__.debug(f'{f"MaxEvaluated":<11}: {maxEvaluatedPoints: >3} <- {maxEvaluatedHand:<16}({maxEvaluatedDice})')

        expected: float = sum(evaluatedPointsList) / len(evaluatedPointsList)
        endTime: float = time.time()

        return (expected, endTime - startTime)

    def choiseReroll(self, dice: Dice, mode: HandChoiseMode, modeBySelf: HandChoiseMode) -> Reroll:
        """振り直すサイコロを選択する

        Args:
            dice (Dice): 現在のサイコロ
            mode (HandChoiseMode): 役選択/評価モード
            modeBySelf (HandChoiseMode): 役選択モード(振り直しなし時)

        Returns:
            Reroll: 振り直し対象
        """
        # 振り直し対象
        retReroll: Reroll = Reroll()
        # 最大評価値
        maxEvaluatedPoints: float = -100
        for bit in range(pow(2, NUM_OF_DICE)):
            reroll: Reroll = Reroll(bit)

            # 振り直しを評価する
            self.__logger__.debug(f'{f"Reroll({bit: >2})":<11}: {str(reroll):<16}')
            (evaluatedPoints, time) = self.evaluateReroll(dice, reroll, mode, modeBySelf)

            self.__logger__.debug(f'{f"Reroll({bit: >2})":<11}: Ave.Expected: {evaluatedPoints: >7.4f} time: {time: >7.4f}')

            # 評価値の高い振り直しを選択する
            if maxEvaluatedPoints < evaluatedPoints:
                maxEvaluatedPoints = evaluatedPoints
                retReroll = reroll

        return retReroll


def main() -> None:
    pass


if __name__ == '__main__':
    main()
