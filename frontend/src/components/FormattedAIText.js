import React from 'react';

const renderInline = (text) => {
  const normalized = text.replace(/\*\*/g, '__DOUBLE_ASTERISK__');
  const parts = normalized.split(/(__DOUBLE_ASTERISK__.*?__DOUBLE_ASTERISK__)/g).filter(Boolean);

  return parts.map((part, index) => {
    const boldMatch = part.match(/^__DOUBLE_ASTERISK__(.*?)__DOUBLE_ASTERISK__$/);
    if (boldMatch) {
      return <strong key={index} className="font-semibold text-gray-900">{boldMatch[1]}</strong>;
    }

    return part.replace(/__DOUBLE_ASTERISK__/g, '**');
  });
};

const normalizeLine = (line) => line.replace(/\r/g, '').trim();

const FormattedAIText = ({ text, clamp = false }) => {
  if (!text) return null;

  const lines = String(text).split('\n');
  const elements = [];
  let paragraphLines = [];
  let listItems = [];

  const flushParagraph = () => {
    if (!paragraphLines.length) return;
    const paragraphText = paragraphLines.join(' ');
    elements.push(
      <p key={`p-${elements.length}`} className={clamp ? 'line-clamp-3' : 'leading-7'}>
        {renderInline(paragraphText)}
      </p>
    );
    paragraphLines = [];
  };

  const flushList = () => {
    if (!listItems.length) return;
    elements.push(
      <ul key={`ul-${elements.length}`} className="list-disc space-y-1 pl-5">
        {listItems.map((item, index) => (
          <li key={`li-${index}`}>{renderInline(item)}</li>
        ))}
      </ul>
    );
    listItems = [];
  };

  lines.forEach((rawLine) => {
    const line = normalizeLine(rawLine);

    if (!line) {
      flushParagraph();
      flushList();
      return;
    }

    const bulletMatch = line.match(/^[-*]\s+(.*)$/);
    if (bulletMatch) {
      flushParagraph();
      listItems.push(bulletMatch[1]);
      return;
    }

    if (/^\*\*.*\*\*$/.test(line) && line.length <= 120) {
      flushParagraph();
      flushList();
      elements.push(
        <h4 key={`h-${elements.length}`} className="pt-1 text-sm font-semibold text-gray-900">
          {renderInline(line)}
        </h4>
      );
      return;
    }

    flushList();
    paragraphLines.push(line);
  });

  flushParagraph();
  flushList();

  return <div className="space-y-3 text-sm text-gray-700">{elements}</div>;
};

export default FormattedAIText;
