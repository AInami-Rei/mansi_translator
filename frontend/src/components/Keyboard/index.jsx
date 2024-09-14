import React, {useState, useMemo} from 'react';
import RSKeyboard from 'react-simple-keyboard';
import 'react-simple-keyboard/build/css/index.css';
import styles from './index.module.scss';
import cn from 'classnames';

const customLayout = {
  default: [
    'ё 1 2 3 4 5 6 7 8 9 0',
    'й ц у к е н г ш щ з х ъ',
    'ф ы в а п р о л д ж э',
    'я ч с м и т ь б ю',
    '{shift} {space} {alt} {bksp}'
  ],
  defaultShift: [
    'Ё ! " № ; % : ? * ( )',
    'Й Ц У К Е Н Г Ш Щ З Х Ъ',
    'Ф Ы В А П Р О Л Д Ж Э',
    'Я Ч С М И Т Ь Б Ю',
    '{shift} {space} {alt} {bksp}'
  ],
  alt: [
    'ӛ          ',
    'ә ӱ ў ӄ қ ң    ҳ ӽ є̈',
    '  ӓ ӑ ө ӈ о̆ ԯ ԓ ԑ є',
    'я̆ ӌ ҷ ӫ̆ ӧ ӫ ө̆ ю̆ ԑ̈',
    '{shift} {space} {alt} {bksp}'
  ],
  altShift: [
    'Ӛ          ',
    'Ә Ӱ Ў Ӄ Қ Ң    Ҳ Ӽ Є̈',
    '  Ӓ Ӑ Ө Ӈ О̆ Ԯ Ԓ Ԑ Є',
    'Я̆ Ӌ Ҷ Ӫ̆ Ӧ Ӫ Ө̆ Ю̆ Ԑ̈',
    '{shift} {space} {alt} {bksp}'
  ],
};

const Keyboard = ({
  onKeyPress=()=>{},
  onBackspace=()=>{},
  className=''
}) => {
  const [isShift, setIsShift] = useState(false);
  const [isAlt, setIsAlt] = useState(false);

  const keyboardClass = cn(styles.keyboard, className)

  const handleShift = () => {
    setIsShift(!isShift);
  };

  const handleAlt = () => {
    setIsAlt(!isAlt);
  };

  const handleBackspace = () => {
    onBackspace();
  };

  const handleSpace = () => {
    onKeyPress(' ');
  };

  const handlers = {
    '{shift}': handleShift,
    '{alt}': handleAlt,
    '{bksp}': handleBackspace,
    '{space}': handleSpace,
  };

  const handleKeyPress = (button) => {
    const handler = handlers[button];
    if (handler) {
      handler();
      return;
    }
    onKeyPress(button);
  };

  const layoutName = useMemo(() => {
    if (isShift) 
      return isAlt ? 'altShift' : 'defaultShift';
    return isAlt ? 'alt' : 'default';
  }, [isShift, isAlt]);

  return (
    <div className={keyboardClass}>
      <RSKeyboard
        layout={customLayout}
        layoutName={layoutName}
        onKeyPress={handleKeyPress}
      />
    </div>
  );
};

export default Keyboard;
