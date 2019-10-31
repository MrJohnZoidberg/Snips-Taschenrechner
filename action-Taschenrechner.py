#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
import toml
import math
import random


USERNAME_INTENTS = "domi"
MQTT_BROKER_ADDRESS = "localhost:1883"
MQTT_USERNAME = None
MQTT_PASSWORD = None


def add_prefix(intent_name):
    return USERNAME_INTENTS + ":" + intent_name


def msg_addition(hermes, intent_message):
    first, second = get_terms(intent_message)
    sentence = f"{first} plus {second} ergibt {num_to_words(first + second)} ."
    end_session(hermes, intent_message, sentence)


def msg_subtraktion(hermes, intent_message):
    first, second = get_terms(intent_message)
    sentence = f"{first} minus {second} ergibt {num_to_words(first - second)} ."
    end_session(hermes, intent_message, sentence)


def msg_multiplikation(hermes, intent_message):
    first, second = get_terms(intent_message)
    sentence = f"{first} mal {second} ergibt {num_to_words(first * second)} ."
    end_session(hermes, intent_message, sentence)


def msg_division(hermes, intent_message):
    first, second = get_terms(intent_message)
    if second == 0:
        end_session(hermes, intent_message, "Ich kann leider nicht durch Null teilen.")
        return
    sentence = f"{first} durch {second} ergibt {num_to_words(first / second)} ."
    end_session(hermes, intent_message, sentence)


def msg_wurzel(hermes, intent_message):  # TODO: Only english words
    first = int(intent_message.slots.firstTerm.first().value)
    sentence = f"Die Wurzel aus {first} ist {num_to_words(math.sqrt(first))} ."
    end_session(hermes, intent_message, sentence)


def msg_zufall(hermes, intent_message):
    item = intent_message.slots.item_random.first().value
    if item == 'coin' or item == 'kopf ' or item == 'münze ':
        coin_random = random.randrange(0, 1)
        if coin_random == 0:
            sentence = "Es ist ein Kopf."
        else:
            sentence = "Es ist eine Zahl."
    elif item == 'dice' or item == 'würfel ':
        dice_random = random.randrange(1, 6)
        sentence = "Ich habe eine {number} gewürfelt.".format(number=dice_random)
    elif item == 'number' or item == 'zahl ':
        number_random = random.randrange(0, 1000)
        sentence = "Die {number} habe ich gerade zufällig gewählt.".format(number=number_random)
    # TODO: random number from range
    else:
        sentence = "Diese Funktion ist noch nicht verfügbar."
    end_session(hermes, intent_message, sentence)


def get_terms(intent_message):
    first = int(intent_message.slots.firstTerm.first().value)
    second = int(intent_message.slots.secondTerm.first().value)
    return first, second


def num_to_words(num):
    if isinstance(num, float):
        if num % 1 == 0:
            words = str(int(num))
        else:
            pre, post = str(num).split('.')
            words = f"{pre} komma {post}"
    else:
        words = str(num)
    return words


def end_session(hermes, intent_message, text):
    hermes.publish_end_session(intent_message.session_id, text)


if __name__ == "__main__":
    snips_config = toml.load('/etc/snips.toml')
    if 'mqtt' in snips_config['snips-common'].keys():
        MQTT_BROKER_ADDRESS = snips_config['snips-common']['mqtt']
    if 'mqtt_username' in snips_config['snips-common'].keys():
        MQTT_USERNAME = snips_config['snips-common']['mqtt_username']
    if 'mqtt_password' in snips_config['snips-common'].keys():
        MQTT_PASSWORD = snips_config['snips-common']['mqtt_password']

    with Hermes(MQTT_BROKER_ADDRESS) as h:
        h.subscribe_intent(add_prefix("getAddition"), msg_addition)
        h.subscribe_intent(add_prefix("getSubtraktion"), msg_subtraktion)
        h.subscribe_intent(add_prefix("getMultiplikation"), msg_multiplikation)
        h.subscribe_intent(add_prefix("getDivision"), msg_division)
        h.subscribe_intent(add_prefix("getWurzel"), msg_wurzel)
        h.subscribe_intent(add_prefix("getZufall"), msg_zufall)
        h.start()
