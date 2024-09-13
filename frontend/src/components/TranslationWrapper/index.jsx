import React, { useState, useEffect, useRef } from 'react';
import TextInput from '../TextInput';
import Keyboard from '../Keyboard';
import styles from './index.module.scss'
import SwapLanguagesButton from '../SwapLanguagesButton';
import { apiService } from '../../apiService';


const MAX_CHAR_LIMIT = 250;

const placeholders = {"Русский": "Введите текст", "Мансийский": "Несов текст"}
const abbreviations = {"Русский": "ru", "Мансийский": "ms"}

const TranslationBox = () => {
  const [inputText, setInputText] = useState('');
  const [translation, setTranslation] = useState('');
  const [isKeyboardOpen, setIsKeyboardOpen] = useState(false);
  const [languages, setLanguages] = useState({
    from: 'Русский',
    to: 'Мансийский'
  });
  const [isLoading, setIsLoading] = useState(false);
  const timeoutRef = useRef(null);

  const handleTranslate = async (text) => {
    setTranslation('');
    setIsLoading(true);
    try {
      const response = await apiService.translate(
        text,
        abbreviations[languages.from],
        abbreviations[languages.to]
      )

      setTranslation(response.data['text'])

    } catch (error) {
        console.error('Ошибка:', error);
      }

    setIsLoading(false);
  };

  const handleInputChange = (text) => {
    setInputText(text);
    setTranslation('')

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      text.trim() && handleTranslate(text);
    }, 1000);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleSwapLanguages = () => {
    setLanguages({
      from: languages.to,
      to: languages.from
    });
    setTranslation('');
    setInputText('')
  };

  const handleClearInput = () => {
    setIsLoading(false);
    setInputText('');
    setTranslation('');
  };

  const handleKeyboardKeyPress = (key) => {
    handleInputChange(inputText + key);
  }

  const handleKeyboardBackspace = () => {
    handleInputChange(inputText.slice(0, -1));
  }

  const onKeyboardClick = () => setIsKeyboardOpen(!isKeyboardOpen)

  return (
    <>
    <div className={styles.translationBox}>
      <div className={styles.header}>
        <div className={styles.languageBox}>{languages.from}</div>
        <SwapLanguagesButton onClick={handleSwapLanguages} />
        <div className={styles.languageBox}>{languages.to}</div>
      </div>

      <div className={styles.content}>
        <TextInput
          className={styles.sourceLang}
          value={inputText}
          onChange={handleInputChange}
          onClear={handleClearInput}
          onKeyboardClick={onKeyboardClick}
          charCount={inputText.length}
          maxChars={MAX_CHAR_LIMIT}
          placeholder={placeholders[languages.from]}
          isSource
        />

        <TextInput
          className={styles.targetLang}
          value={translation}
          isLoading={isLoading}
        />
      </div>
    </div>
    {isKeyboardOpen && <Keyboard
      onKeyPress={handleKeyboardKeyPress}
      onBackspace={handleKeyboardBackspace}
    />}
    </>
  );
};

export default TranslationBox;
