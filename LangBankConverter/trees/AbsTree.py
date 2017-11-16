# This script provides abstract tree representation to facilitate data format conversions.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

from abc import ABCMeta, abstractmethod


class AbsWord:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_form(self): pass

    @abstractmethod
    def set_form(self, form): pass


class AbsSentence:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_words(self, words): pass

    @abstractmethod
    def get_words(self): pass

    @abstractmethod
    def add_word_by_idx(self, idx, word): pass

    @abstractmethod
    def set_word_by_idx(self, idx, word): pass

    @abstractmethod
    def get_word(self, idx, word): pass

    @staticmethod
    @abstractmethod
    def read_from_pml_file(file): pass

    @staticmethod
    @abstractmethod
    def read_from_file(file): pass

    @staticmethod
    @abstractmethod
    def write_to_file(file, sentences): pass
