import React from 'react';
import { GoArrowSwitch } from "react-icons/go";

import styles from './index.module.scss';

const SwapLanguagesButton = ({ onClick }) => {
  return (
    <button className={styles.swapBtn} onClick={onClick}>
      <GoArrowSwitch className={styles.swapIcon} />
    </button>
  );
};

export default SwapLanguagesButton;
