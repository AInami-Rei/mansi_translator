import React from 'react';
import TranslationWrapper from './components/TranslationWrapper';
import styles from './index.module.scss'
import logo from './assets/logo (2).svg'

const App = () => {
  return (
    <div className={styles.app}>
      <div className={styles.appHeader}>
        <img className={styles.logo} src={logo} alt="" />
        <p className={styles.headerText}>ёлымтан переводчик</p>
      </div>
      <TranslationWrapper />
    </div>
  );
}

export default App;