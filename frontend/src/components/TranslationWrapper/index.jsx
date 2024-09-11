import React, { useState, useMemo, useEffect } from 'react';
import TextInput from '../TextInput';
import Keyboard from '../Keyboard';
import styles from './index.module.scss'
import SwapLanguagesButton from '../SwapLanguagesButton';
import { debounce } from 'lodash';
import {observer} from 'mobx-react-lite'
import { useStores } from "../../stores/rootStore";


const MAX_CHAR_LIMIT = 250;

const placeholders = {"Русский": "Введите текст", "Мансийский": "Несов текст"}

const TranslationBox = observer(() => {
  const [inputText, setInputText] = useState('');
  const [translation, setTranslation] = useState('');
  const [languages, setLanguages] = useState({
    from: 'Русский',
    to: 'Мансийский'
  });
  const [isLoading, setIsLoading] = useState(false);

  const {keyboardStore} = useStores()

  const handleTranslate = async (text) => {
    setTranslation('');
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000))
    console.log('Запрос на перевод:', text);
    setTranslation('Павыл ворт унли. Ман вор павылт олэв.');
    setIsLoading(false);
  };

  const debouncedTranslate = useMemo(() => debounce(handleTranslate, 1000), []);

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
      if (navigator && navigator.clipboard && navigator.clipboard.writeText)
        navigator.clipboard.writeText(translation);
    }
  };

  const handleSwapLanguages = () => {
    setLanguages({
      from: languages.to,
      to: languages.from
    });
    setTranslation('');
    setInputText('')
  };

  const handleClearInput = () => {
    debouncedTranslate.cancel();
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

  const onKeyboardClick = () => keyboardStore.setIsOpen(!keyboardStore.isOpen)

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
          onClear={handleCopy}
          isLoading={isLoading}
        />
      </div>
    </div>
    {keyboardStore.isOpen && <Keyboard
      onKeyPress={handleKeyboardKeyPress}
      onBackspace={handleKeyboardBackspace}
    />}
    </>
  );
});

export default TranslationBox;