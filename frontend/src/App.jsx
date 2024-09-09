import React from 'react';
import TranslationWrapper from './components/TranslationWrapper';
import styles from './index.module.scss'

function App() {
  return (
    <div className={styles.app}>
      <TranslationWrapper />
    </div>
  );
}

export default App;