import React from 'react';
import { FiRefreshCw } from 'react-icons/fi';
import cn from 'classnames';

import styles from './index.module.scss';

const copyToClipboard = (text) => {
  const textarea = document.createElement('textarea');

  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  textarea.style.left = '-9999px';

  textarea.value = text;

  document.body.appendChild(textarea);

  textarea.select();

  document.execCommand('copy')

  document.body.removeChild(textarea);
}


const TextInput = ({ value, className, onChange=()=>{}, onClear=()=>{}, onKeyboardClick=()=>{}, maxLength=250, isSource=false, isLoading=false, placeholder=''}) => {
  const inputClassName = cn(
    styles.textInput,
    className,
  )

  const handleCopy = async () => {
    if (value) {
      copyToClipboard(value)
    }
  };

  return (
    <div className={styles.textInputContainer}>
      <textarea
        className={inputClassName}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
        }}
        placeholder={placeholder}
        disabled={!isSource}
        maxLength={maxLength}
      />

      {isSource && value && <div className={styles.charCount}>{`${value.length} / ${maxLength}`}</div>}
      {isSource &&
        <svg className={styles.keyboardBtn} onClick={onKeyboardClick} viewBox="0 0 15 9" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="0.5" y="0.5" width="14" height="8" rx="0.5" stroke="black"/>
          <rect x="2" y="2" width="2" height="2" rx="0.6" fill="black"/>
          <rect x="5" y="2" width="2" height="2" rx="0.6" fill="black"/>
          <rect x="5" y="5" width="5" height="2" rx="0.6" fill="black"/>
          <rect x="11" y="2" width="2" height="2" rx="0.6" fill="black"/>
          <rect x="2" y="5" width="2" height="2" rx="0.6" fill="black"/>
          <rect x="11" y="5" width="2" height="2" rx="0.6" fill="black"/>
          <rect x="8" y="2" width="2" height="2" rx="0.6" fill="black"/>
        </svg>
      }

      {isSource && value && <button className={styles.clearBtn} onClick={onClear}>✕</button>}
      {!isSource && value && <button className={styles.copyBtn} onClick={handleCopy}>
          <svg className={styles.copyIcon} viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" width="11" height="11" rx="3" fill="#8E8E8E"/>
            <rect y="2" width="11" height="11" rx="3" fill="#BABABA"/>
          </svg>
        </button>}

      {isLoading && !isSource &&
        <FiRefreshCw className={styles.loader} />
        }

    </div>
  );
};

export default TextInput;
