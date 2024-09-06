import React from 'react';

import styles from './index.module.scss';

const index = ({ value, onChange=()=>{}, onClear=()=>{}, maxLength=250, isSource=false, placeholder=''}) => {
  return (
    <div className={styles.textInputContainer}>
      <textarea
        className={styles.textInput}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
        }}
        placeholder={placeholder}
        disabled={!isSource}
        maxLength={maxLength}
      />

      {isSource && value && <div className={styles.charCount}>{`${value.length} / ${maxLength}`}</div>}

      {isSource && value && <button className={styles.clearBtn} onClick={onClear}>✕</button>}
      {!isSource && value && <button className={styles.copyBtn} onClick={onClear}>
          <svg className={styles.copyIcon} viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" width="11" height="11" rx="3" fill="#8E8E8E"/>
            <rect y="2" width="11" height="11" rx="3" fill="#BABABA"/>
          </svg>
        </button>}
      
    </div>
  );
};

export default index;