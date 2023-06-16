import json
import os
import random
import sys
import io
import argparse

log_stream = io.StringIO()


class TeeStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


stdout_orig = sys.stdout
log_file = open("logs.txt", "a")
tee_stream = TeeStream(stdout_orig, log_stream, log_file)
sys.stdout = tee_stream


class Cards:

    def __init__(self):
        self.set_of_terms = set()
        self.set_of_definitions = set()
        self.dct_with_cards = {}
        if args.import_from is not None:
            if os.path.exists(args.import_from):
                with open(args.import_from, 'r') as f:
                    cards_from_file = json.load(f)
                    self.dct_with_cards.update(cards_from_file)
                    print(f'{len(cards_from_file)} cards have been loaded')
            else:
                print('File not found.')

    def menu(self):
        functions = {'add': self.add_card,
                     'remove': self.remove_card,
                     'import': self.import_card,
                     'export': self.export_card,
                     'ask': self.ask,
                     'exit': self.exit_program,
                     'log': self.log_files,
                     'hardest card': self.hardest_card,
                     'reset stats': self.reset_stats}
        while True:
            print('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
            functions[input()]()

    @staticmethod
    def log_files():
        print('File name:')
        f_name = input()
        with open(f_name, "a") as file:
            file.write(log_stream.getvalue())
        print('The log has been saved.')

    def hardest_card(self):
        if self.dct_with_cards:
            most_mistakes = max(v[1] for v in self.dct_with_cards.values())
        else:
            most_mistakes = 0
        tmp_list = [k for k, v in self.dct_with_cards.items() if v[1] == most_mistakes]
        if len(tmp_list) == 0 or most_mistakes == 0:
            print('There are no cards with errors.')
        elif len(tmp_list) == 1:
            print(f'The hardest card is "{tmp_list[0]}". You have {most_mistakes} errors answering it')
        else:
            tmp_list = ", ".join(s for s in tmp_list)
            print(f'The hardest card are "{tmp_list}". You have {most_mistakes} errors answering it')

    def reset_stats(self):
        for k in self.dct_with_cards.keys():
            self.dct_with_cards.get(k)[1] = 0
        print('Card statistics have been reset.')

    def add_card(self):
        term = self.new_term()
        definition = self.new_definition()
        self.dct_with_cards.setdefault(term, definition)
        print(f'The pair ("{term}":"{definition[0]}") has been added.')

    def remove_card(self):
        print('Which card?')
        card_for_remove = input()
        if card_for_remove in self.dct_with_cards:
            self.dct_with_cards.pop(card_for_remove)
            print('The card has been removed.')
        else:
            print(f'Can\'t remove "{card_for_remove}": there is no such card.')

    def import_card(self):
        print('File name:')
        file_name = input()
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                cards_from_file = json.load(f)
                self.dct_with_cards.update(cards_from_file)
                print(f'{len(cards_from_file)} cards have been loaded')
        else:
            print('File not found.')

    def export_card(self):
        print('File name:')
        file_name = input()
        with open(file_name, 'a') as f:
            f.write(json.dumps(self.dct_with_cards))
        print(f'{len(self.dct_with_cards)} cards have been saved.')

    def exit_program(self):
        if args.export_to is not None:
            with open(args.export_to, 'a') as f:
                f.write(json.dumps(self.dct_with_cards))
            print(f'{len(self.dct_with_cards)} cards have been saved.')
        print('Bye bye!')
        sys.exit()

    def ask(self):
        amount = int(input('How many times to ask?'))
        while amount > 0:
            rand_card = random.choice(list(self.dct_with_cards.keys()))
            print(f'Print the definition of "{rand_card}":')
            user_answer = input()
            amount -= 1
            if user_answer == self.dct_with_cards[rand_card][0]:
                print('Correct!')
            else:
                card_with_user_answer = ''
                for k, v in self.dct_with_cards.items():
                    if v[0] == user_answer:
                        card_with_user_answer = k
                        break
                if card_with_user_answer:
                    self.dct_with_cards[rand_card][1] += 1
                    print(f'Wrong. The right answer is "{self.dct_with_cards[rand_card][0]}"'
                          f', but your definition is correct for '
                          f'"{card_with_user_answer}".')
                else:
                    self.dct_with_cards[rand_card][1] += 1
                    print(f'Wrong. The right answer is "{self.dct_with_cards[rand_card][0]}".')

    def new_term(self):
        print('The card:')
        while True:
            term = input()
            if term not in self.set_of_terms:
                self.set_of_terms.add(term)
                return term
            else:
                print(f'The term "{term}" already exists. Try again:')

    def new_definition(self):
        print(f'The definition of the card:')
        while True:
            definition = input()
            if definition not in self.set_of_definitions:
                self.set_of_definitions.add(definition)
                definition = [definition, 0]
                return definition
            else:
                print(f'The definition "{definition}" already exists. Try again:')


parser = argparse.ArgumentParser()
parser.add_argument("--import_from")
parser.add_argument("--export_to")
args = parser.parse_args()

card = Cards()
card.menu()

log_file.close()
sys.stdout = stdout_orig
