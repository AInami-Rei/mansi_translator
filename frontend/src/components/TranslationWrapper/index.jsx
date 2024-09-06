import React, { useState, useMemo, useEffect } from 'react';
import TextInput from '../TextInput';
import Keyboard from '../Keyboard';
import styles from './index.module.scss'
import SwapLanguagesButton from '../SwapLanguagesButton';
import { debounce } from 'lodash';

const MAX_CHAR_LIMIT = 250;

const placeholders = {"Русский": "Введите текст", "Мансийский": "Несов текст"}

const TranslationBox = () => {
  const [inputText, setInputText] = useState('');
  const [translation, setTranslation] = useState('');
  const [languages, setLanguages] = useState({
    from: 'Русский',
    to: 'Мансийский'
  });

  // Функция для перевода текста (заменить на реальный API запрос)
  const handleTranslate = (text) => {
    console.log('Запрос на перевод:', text);
    // Пример результата перевода, который вы могли бы получить от API
    setTranslation('Павыл ворт унли. Ман вор павылт олэв.');
  };

  const debouncedTranslate = useMemo(() => debounce(handleTranslate, 2000), []);

  const handleInputChange = (text) => {
    setInputText(text);
    if (text.trim()) {
      debouncedTranslate(text);
    } else {
      debouncedTranslate.cancel();
      setTranslation('');
    }
  };

  useEffect(() => {
    return () => {
      debouncedTranslate.cancel();
    };
  }, [debouncedTranslate]);

  const handleCopy = () => {
    if (translation) {
      navigator.clipboard.writeText(translation);
      alert('Текст скопирован в буфер обмена!');
    }
  };

  const handleSwapLanguages = () => {
    setLanguages({
      from: languages.to,
      to: languages.from
    });
    setTranslation('');
  };

  const handleClearInput = () => {
    setInputText('');
    setTranslation('');
  };

  const handleKeyboardKeyPress = (key) => {
    setInputText(inputText + key);
  }

  const handleKeyboardBackspace = () => {
    setInputText(inputText.slice(0, -1));
  }

  return (
    <div className={styles.translationBox}>
      <div className={styles.header}>
        <SwapLanguagesButton onClick={handleSwapLanguages} />
        <div className={styles.languageBox}>{languages.from}</div>
        <div className={styles.languageBox}>{languages.to}</div>
      </div>

      <div className={styles.content}>
        <TextInput
          className={styles.sourceLang}
          value={inputText}
          onChange={handleInputChange}
          onClear={handleClearInput}
          charCount={inputText.length}
          maxChars={MAX_CHAR_LIMIT}
          placeholder={placeholders[languages.from]}
          isSource
        />

        <TextInput
          className={styles.targetLang}
          value={translation}
          onClear={handleCopy}
        />
      </div>

      <Keyboard
        isOpen // TODO by button
        onKeyPress={handleKeyboardKeyPress}
        onBackspace={handleKeyboardBackspace}
      />
    </div>
  );
};

export default TranslationBox;