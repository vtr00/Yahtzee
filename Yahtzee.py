import copy
import random
from enum import Enum
import time

# 定数定義
MIN_OF_PIP: int = 1
MAX_OF_PIP: int = 6
NUM_OF_DICE: int = 5

class Die:
    """サイコロ1個を表現するクラス
    """
    def __init__(self, pip: int = -1):
        """コンストラクタ

        Args:
            pip (int, optional): サイコロの値. Defaults to -1.
        """
        self.__pip__: int = -1 # サイコロの値

        if pip == -1:
            self.Roll()
        else:
            self.SetPip(pip)
    
    def __str__(self) -> str:
        """文字列化関数

        Returns:
            str: 文字列
        """
        return str(self.__pip__)
    
    def __repr__(self) -> str:
        return f"{ self.__class__.__name__ }({ repr(self.__pip__) })"
    
    def Pip(self) -> int:
        """サイコロの目を取得する

        Returns:
            int: サイコロの目
        """
        return self.__pip__
    
    def SetPip(self, pip: int) -> None:
        """サイコロの目を設定する

        Args:
            pip (int): サイコロの目
        """
        assert 1 <= pip and pip <= MAX_OF_PIP
        self.__pip__ = pip

    def Roll(self) -> None:
        """サイコロを振り直す
        """
        self.SetPip(random.randint(MIN_OF_PIP, MAX_OF_PIP))

class Dice:
    """サイコロ5個を表現する
    """
    def __init__(self, pips: list[int] = [-1, -1, -1, -1, -1]):
        """コンストラクタ

        Args:
            pips (list[int]): サイコロの目の初期値のリスト
        """
        assert NUM_OF_DICE == len(pips)

        self.__dice__: list[Die] = [Die(pip) for pip in pips] # サイコロリスト
        self.Sort()

    def __iter__(self):
        return self.__dice__.__iter__()

    def __str__(self) -> str:
        return str(self.Pips())

    def __repr__(self) -> str:
        return f"{ self.__class__.__name__ }({ repr((self.Pips()) )})"

    def Sort(self) -> None:
        """サイコロの目の昇順に並び替える
        """
        self.__dice__.sort(key=Die.Pip)

    def Pips(self) -> list[int]:
        """サイコロの目をリストで取得する

        Returns:
            list[int]: サイコロの目のリスト
        """
        pips: list[int] = [die.Pip() for die in self.__dice__]
        return pips

    def SetPips(self, pips: list[int]) -> None:
        """サイコロの目をリストで指定する

        Args:
            pips (list[int]): サイコロの目のリスト
        """
        self.__init__(pips)
        # assert NUM_OF_DICE == len(pips)

        # self.__dice__: list[Die] = [Die(pip) for pip in pips]
        # self.Sort()

    def GetReroll(self, pips: list[int]) -> list[int]:
        """どのサイコロの目を振り直す必要があるかを取得する

        Args:
            pips (list[int]): 目標とするサイコロの目

        Returns:
            list[int]: 振り直し対象のリスト
        """
        lpips: list[int] = self.Pips()
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

    def Roll(self, indexes: list[int] = []) -> None:
        """指定のサイコロを振り直す

        Args:
            indexes (list[int], optional): 振り直す対象のサイコロ. Defaults to [].
        """
        if len(indexes) == 0: # 指定がなければすべて降り直し
            for die in self.__dice__:
                die.Roll()
        else:
            for index in indexes:
                assert 0 <= index and index <= len(self.__dice__) - 1
                self.__dice__[index].Roll()
        self.Sort()

Hands = Enum('Hand', ['Ace', 'Duce', 'Tri', 'Four', 'Five', 'Six', 'Choise', 'FourDice', 'FullHouse', 'SStraight', 'BStraight', 'Yahtzee'])
"""役
"""

class Calculator:
    """役ごとの点数を計算する
    """

    def __countif__(self, dice: Dice, num: int) -> int:
        """引数と一致する値の個数を返す

        Args:
            dice (Dice): 確認するサイコロ
            num (int): 確認する値

        Returns:
            int: 一致する値の個数
        """
        count: int = sum(pip == num for pip in dice.Pips())
        return count

    def __is_four_dice__(self, dice: Dice) -> bool:
        """FourDiceかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        match: int = 0
        count: int = 0
        for pip in dice.Pips():
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
    
    def __is_full_house__(self, dice: Dice) -> bool:
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

        for pip in dice.Pips():
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

        # 2,3の組み合わせならFullHouse
        if count1 * count2 == 6:
            return True

        return False
    
    def __is_s_straight__(self, dice: Dice) -> bool:
        """S.Straightかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        match: int = 0
        count: int = 0

        for pip in dice.Pips():
            if match == 0:
                match = pip
                count = 1
            elif match + 1 == pip:
                match += 1
                count += 1
        
        return 4 <= count
    
    def __is_b_straight__(self, dice: Dice) -> bool:
        """B.Straghtかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        match: int = 0
        count: int = 0

        for pip in dice.Pips():
            if match == 0:
                match = pip
                count = 1
            elif match + 1 == pip:
                match = pip
                count += 1
            else:
                return False
        return True
    
    def __is_yahtzee__(self, dice: Dice) -> bool:
        """Yahtzeeかどうかを判定する

        Args:
            dice (Dice): 確認するサイコロ

        Returns:
            bool: 確認結果
        """
        matches: int = 0
        for pip in dice.Pips():
            # 1つでも一致しなければYahtzeeではない
            if matches == 0:
                matches = pip
            elif matches != pip:
                return False
        return True

    def CalculatePoints(self, hand: Hands, dice: Dice):
        """指定された役での点数を計算する

        Args:
            hand (Hands): 役
            dice (Dice): サイコロ

        Returns:
            _type_: 点数
        """
        match hand:
            case Hands.Ace:
                return self.__countif__(dice, 1) * 1
            case Hands.Duce:
                return self.__countif__(dice, 2) * 2
            case Hands.Tri:
                return self.__countif__(dice, 3) * 3
            case Hands.Four:
                return self.__countif__(dice, 4) * 4
            case Hands.Five:
                return self.__countif__(dice, 5) * 5
            case Hands.Six:
                return self.__countif__(dice, 6) * 6
            case Hands.Choise:
                return sum(dice.Pips())
            case Hands.FourDice:
                return sum(dice.Pips()) if self.__is_four_dice__(dice) else 0
            case Hands.FullHouse:
                return sum(dice.Pips()) if self.__is_full_house__(dice) else 0
            case Hands.SStraight:
                return 15 if self.__is_s_straight__(dice) else 0
            case Hands.BStraight:
                return 30 if self.__is_b_straight__(dice) else 0
            case Hands.Yahtzee:
                return 50 if self.__is_yahtzee__(dice) else 0
    
    def GetBestPoints(self, hand: Hands) -> int:
        """指定された役での最大点数を取得する

        Args:
            hand (Hands): 役

        Returns:
            int: 最大点数
        """
        match hand:
            case Hands.Ace:
                # Dice([1,1,1,1,1])
                return 5
            case Hands.Duce:
                # Dice([2,2,2,2,2])
                return 10
            case Hands.Tri:
                # Dice([3,3,3,3,3])
                return 15
            case Hands.Four:
                # Dice([4,4,4,4,4])
                return 20
            case Hands.Five:
                # Dice([5,5,5,5,5])
                return 25
            case Hands.Six:
                # Dice([6,6,6,6,6])
                return 30
            case Hands.Choise:
                # Dice([6,6,6,6,6])
                return 30
            case Hands.FourDice:
                # Dice([6,6,6,6,6])
                return 30
            case Hands.FullHouse:
                # Dice([5,5,6,6,6])
                return 28
            case Hands.SStraight:
                return 15
            case Hands.BStraight:
                return 30
            case Hands.Yahtzee:
                return 50

class Field:
    """場
    """

    def __init__(self):
        """コンストラクタ
        """
        self.__calculator__: Calculator = Calculator()
        self.__field_dice__: dict[Hands, Dice | None] = {
            Hands.Ace : None, Hands.Duce : None, Hands.Tri : None, Hands.Four : None, Hands.Five : None, Hands.Six : None, 
            Hands.Choise : None, Hands.FourDice : None, Hands.FullHouse : None, Hands.SStraight : None, Hands.BStraight : None, Hands.Yahtzee : None
        }
        self.__none_hands__: list[Hands] = [
            Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six,
            Hands.Choise, Hands.FourDice, Hands.FullHouse, Hands.SStraight, Hands.BStraight, Hands.Yahtzee
        ]
        self.__field_points__: dict[Hands, int] = {
            Hands.Ace : 0, Hands.Duce : 0, Hands.Tri : 0, Hands.Four : 0, Hands.Five : 0, Hands.Six : 0, 
            Hands.Choise : 0, Hands.FourDice : 0, Hands.FullHouse : 0, Hands.SStraight : 0, Hands.BStraight : 0, Hands.Yahtzee : 0
        }
        self.__bonus__: int = 0

    def GetNoneHands(self) -> list[Hands]:
        """未割り当ての役一覧を取得する

        Returns:
            list[Hands]: 未割り当ての役
        """
        return self.__none_hands__

    def SetDice(self, hand: Hands, dice: Dice, isForce: bool = False):
        """役にサイコロを割り当てる

        Args:
            hand (Hands): 役
            dice (Dice): サイコロ
            isForce (bool, optional): 既に役が割り当てられていても上書きするか. Defaults to False.
        """
        assert isForce or hand in self.__none_hands__

        self.__field_dice__[hand] = copy.deepcopy(dice)
        self.__field_points__[hand] = self.__calculator__.CalculatePoints(hand, dice)
        self.__none_hands__.remove(hand)

        if self.__bonus__ == 0 and hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]:
            self.__bonus__ = 35 if 63 <= self.__num_sum__() else 0

    def __num_sum__(self) -> int:
        """数字役の合計点を取得する

        Returns:
            int: 数字役の合計点
        """
        sums: int = sum([self.__field_points__[hand] for hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]])
        return sums

    def Sum(self) -> int:
        """合計点を取得する

        Returns:
            int: 合計点
        """
        sums: int = sum(self.__field_points__.values())
        sums += self.__bonus__
        return sums
    
    def SumIfSetDice(self, hand: Hands, dice: Dice) -> tuple[int, int]:
        """役にサイコロを設定したときの合計点を取得する

        Args:
            hand (Hands): 役
            dice (Dice): サイコロ

        Returns:
            int: 役にサイコロを設定したときの合計点
            int: 追加される点
        """
        sums: int = self.Sum()
        handPoints: int = self.__calculator__.CalculatePoints(hand, dice)
        bonusPoints: int = 0
        if self.__bonus__ == 0 and hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]:
            bonusPoints = 35 if 63 <= self.__num_sum__() + handPoints else 0
        sums += handPoints + bonusPoints
        return (sums, handPoints + bonusPoints)


    def Print(self):
        """フィールドの状態をディスプレイに表示する
        """
        for hand in [Hands.Ace, Hands.Duce, Hands.Tri, Hands.Four, Hands.Five, Hands.Six]:
            value = self.__field_points__[hand]
            print(f'{hand.name:<15}: {value:>3} <- { self.__field_dice__[hand] }')

        print(f'{"(BonusEval)":<15}: {self.__num_sum__():>3}')
        value: int = self.__bonus__
        print(f'{"Bonus":<15}: {value:>3}')

        for hand in [Hands.Choise, Hands.FourDice, Hands.FullHouse, Hands.SStraight, Hands.BStraight, Hands.Yahtzee]:
            value: int = self.__field_points__[hand]
            print(f'{hand.name:<15}: {value:>3} <- { self.__field_dice__[hand] }')
        print(f'{"Sum":<15}: {self.Sum():>3}')

class Evaluator:
    """場とサイコロを評価する
    """
    def __init__(self, field: Field, output_expected: bool = False):
        """コンストラクタ

        Args:
            field (Field): フィールド
        """
        self.__field__: Field = copy.deepcopy(field) # 場
        self.__pipsGainPointsPairList__: dict[str, float] = {} # 出目ごとの取得点数の期待値
        self.__output_expected__: bool = output_expected # 評価値を出力するか
    
    def __bit_check__(self, bit: int, index: int) -> bool:
        """特定のビットが立っているかを確認する

        Args:
            bit (int): 数値(2の累乗の和)
            index (int): 確認するビット

        Returns:
            bool: 確認結果
        """
        return (bit // pow(2, index)) % 2 == 1
    
    def __to_bit__(self, indexList: list[int]) -> int:
        """2の累乗の和に変換する

        Args:
            indexList (list[int]): ビットを立てる位置のリスト

        Returns:
            int: 数値
        """
        ret: int = sum([pow(2, index) for index in indexList])
        return ret

    def ChoiseHand(self, dice: Dice) -> tuple[Hands, int]:
        """役を選択する

        Args:
            dice (Dice): 現在のサイコロ

        Returns:
            tuple[Hands, int]: [役, 取得点]
        """
        # 取得点-損失点が最大となる役を選ぶ
        retHand: Hands = Hands.Ace
        bestRate: int = -100
        bestGainPoints: int = -1

        calculator: Calculator = Calculator()
        for hand in self.__field__.GetNoneHands():
            # 現在の役を設定することで獲得するポイント
            (_, gainPoints) = self.__field__.SumIfSetDice(hand, dice)
            assert 0 <= gainPoints
            
            # 現在の役で得られる最大得点との差分ポイント
            handPoints: int = calculator.CalculatePoints(hand, dice)
            bestPoints: int = calculator.GetBestPoints(hand)
            lostPoints: int = bestPoints - handPoints
            assert 0 <= lostPoints

            # 獲得ポイントが多く、最大との差分が少ない役を選ぶ
            rate: int = gainPoints - lostPoints
            if bestRate < rate:
                retHand = hand
                bestRate = rate
                bestGainPoints = gainPoints
        
        # どの役も点数が0の場合は取りうる点の最大値が低い役を選ぶ
        if bestGainPoints == 0:
            retHand = Hands.Ace
            minValue = 100

            for hand in self.__field__.GetNoneHands():
                value = calculator.GetBestPoints(hand)
                if value < minValue:
                    retHand = hand
                    minValue = value

        return (retHand, bestGainPoints)

    def EvaluateReroll(self, dice: Dice, bit: int) -> tuple[float, float]:
        """振り直し時の取得点数の期待値を求める

        Args:
            dice (Dice): 振ったサイコロ
            bit (int): 振り直し対象

        Returns:
            float: 振り直し時の取得点数の期待値
            float: 計算時間
        """
        sumGainPoints: int = 0 # 振り直し時の全パターンの取得点数の合計
        count: int = 0 # 振り直しのパターン数
        pips: list[int] = dice.Pips()

        start: float = time.time()

        rng0: range | list[int] = range(1, MAX_OF_PIP+1) if self.__bit_check__(bit, 0) else [pips[0]]
        rng1: range | list[int] = range(1, MAX_OF_PIP+1) if self.__bit_check__(bit, 1) else [pips[1]]
        rng2: range | list[int] = range(1, MAX_OF_PIP+1) if self.__bit_check__(bit, 2) else [pips[2]]
        rng3: range | list[int] = range(1, MAX_OF_PIP+1) if self.__bit_check__(bit, 3) else [pips[3]]
        rng4: range | list[int] = range(1, MAX_OF_PIP+1) if self.__bit_check__(bit, 4) else [pips[4]]
        for pip0 in rng0:
            for pip1 in rng1:
                for pip2 in rng2:
                    for pip3 in rng3:
                        for pip4 in rng4:
                            tmpPips: list[int] = [pip0, pip1, pip2, pip3, pip4]
                            tmpDice = Dice(tmpPips)
                            (_, gainPoints) = self.ChoiseHand(tmpDice)

                            sumGainPoints += gainPoints
                            count += 1

        expected: float = sumGainPoints / count

        return (expected, time.time() - start)

    def ChoiseReroll(self, dice: Dice) -> list[int]:
        """振り直すサイコロを選択する

        Args:
            dice (Dice): 現在のサイコロ

        Returns:
            list[int]: 振り直し対象のリスト
        """
        retReroll: list[int] = []
        maxExpGainPoints: float = 0
        for bit in range(pow(2, NUM_OF_DICE)):
            # 振り直しを評価する
            (expGainPoints, time) = self.EvaluateReroll(dice, bit)

            reroll: list[int] = []
            # 振り直し対象のリストを作成する
            for index in range(NUM_OF_DICE):
                if self.__bit_check__(bit, index):
                    reroll.append(index)
            
            if self.__output_expected__:
                print(f'    {f"Expected({bit: >2})":<11}: {expGainPoints: >7.4f} <- {str(reroll):<16} time: {time: >7.4f}')

            # 期待値の高い振り直しを選択する
            if maxExpGainPoints < expGainPoints:
                maxExpGainPoints = expGainPoints
                retReroll = reroll

        return retReroll

    # サイコロの各出目で何点得られるかを計算する
    def EvaluateAsRoll(self) -> None:
        self.__pipsGainPointsPairList__.clear()

        for pip0 in range(1,MAX_OF_PIP+1):
            for pip1 in range(1,MAX_OF_PIP+1):
                for pip2 in range(1,MAX_OF_PIP+1):
                    for pip3 in range(1,MAX_OF_PIP+1):
                        for pip4 in range(1,MAX_OF_PIP+1):
                            tmpdice = Dice([pip0, pip1, pip2, pip3, pip4]) # 昇順にソート
                            pips = tmpdice.Pips()

                            (_, gainPoints) = self.ChoiseHand(tmpdice)
                            assert 0 <= gainPoints

                            if gainPoints != 0:
                                if str(pips) in self.__pipsGainPointsPairList__:
                                    # 並び替えて同じ出目が得られるならその分確率が上がるため加算する
                                    self.__pipsGainPointsPairList__[str(pips)] += gainPoints
                                else:
                                    self.__pipsGainPointsPairList__[str(pips)] = gainPoints

    # 振り直すサイコロを選択する2
    def ChoiseReroll2(self, dice: Dice) -> list[int]:
        rerollGainPointsPairList: dict[str, float] = {} # 振り直し対象のサイコロと取得点の合計

        # サイコロごとの点数とそのために振り直すサイコロを取得する
        for pips in self.__pipsGainPointsPairList__.keys():
            points = self.__pipsGainPointsPairList__[pips]
            reroll = dice.GetReroll(eval(pips))
            strReroll = str(reroll)

            if strReroll in rerollGainPointsPairList:
                # 同じダイスを振り直して取り得る役の候補が複数ある場合は得られる点の期待値が上がるため加算する
                # TODO: 振らなかったサイコロによって発生した事象までカウントしてしまっているため、不正確
                rerollGainPointsPairList[strReroll] += points
            else:
                rerollGainPointsPairList[strReroll] = points

        # 振り直しをソートする
        sortedReroll = sorted(rerollGainPointsPairList)
        rerollGainPointsPairList = {k: rerollGainPointsPairList[k] for k in sortedReroll}

        # 点数の高い振り直しを取得する
        retReroll: list[int] = []
        maxExpPoints: float = 0.0
        for strReroll in rerollGainPointsPairList:
            reroll: list[int] = eval(strReroll)
            if len(reroll) != 0:
                # 振り直すサイコロの数だけ期待値が下がる
                expPoints: float = rerollGainPointsPairList[strReroll] / pow(6, len(reroll))
            else:
                (_, expPoints) = self.ChoiseHand(dice)
            if maxExpPoints < expPoints:
                retReroll = reroll
                maxExpPoints = expPoints
            
            print(f'    {"Expected":<15}: {expPoints: >11.8f} <- {reroll}')

        return retReroll


#########################################################

def main() -> None:
    field = Field()
    field.Print()
    print()

    for count in range(len(Hands)):
        print(f'=== {count+1:<2}:')
        dice: Dice = Dice()
        evaluator: Evaluator = Evaluator(field)
        # evaluator.EvaluateAsRoll()

        # 1投目
        dice.Roll()
        print(f'  {"Dice1":<15}: {dice}')

        for throw_idx in [2, 3]:
            # n投目のサイコロを決める
            reroll: list[int] = evaluator.ChoiseReroll(dice)
            print(f'  {f"Reroll{throw_idx}":<15}: {reroll}')
            # n投目のサイコロが存在する場合
            if 0 < len(reroll):
                # n投目
                dice.Roll(reroll)
                print(f'  {f"Dice{throw_idx}":<15}: {dice}')

        # 役を決定する
        (hand, _) = evaluator.ChoiseHand(dice)
        field.SetDice(hand, dice)

        print(f'  {"Choise":<15}: {hand.name}')
        field.Print()
        print()

main()