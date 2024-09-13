import React from 'react';

import styles from './index.module.scss';

const SwapLanguagesButton = ({ onClick }) => {
  return (
    <button className={styles.swapBtn} onClick={onClick}>
      <svg className={styles.swapIcon} viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path className={styles.swapIconPath} d="M4 1L1 4.5M1 4.5L4 8M1 4.5H14" stroke="#2F2F45" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path className={styles.swapIconPath} d="M11 10L14 13.5M14 13.5L11 17M14 13.5H1" stroke="#2F2F45" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  );
};

export default SwapLanguagesButton;
