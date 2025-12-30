import { useState } from 'react';

export default function PromptBox() {
  const [input, setInput] = useState('');

  const handleFire = () => {
    console.log('Prompt:', input);
    // Handle your logic here
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleFire();
    }
  };

  return (
    <div className="prompt-box">
      <input
        type="text"
        className="prompt-input"
        placeholder="Add exam details (marking scheme, pattern) or type None"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <button className="fire-btn" onClick={handleFire}>
        Fire
      </button>

      <style>{`
        .prompt-box {
          display: flex;
          gap: 12px;
          align-items: center;
          background: #0f0f0f;
          border: 1px solid #1f1f1f;
          border-radius: 12px;
          padding: 8px;
          transition: all 0.2s;
        }

        .prompt-box:focus-within {
          border-color: #4a4a4a;
          background: #151515;
        }

        .prompt-input {
          flex: 1;
          background: transparent;
          border: none;
          padding: 12px 16px;
          color: #ffffff;
          font-size: 14px;
        }

        .prompt-input::placeholder {
          color: #4a4a4a;
        }

        .prompt-input:focus {
          outline: none;
        }

        .fire-btn {
          background: #ffffff;
          color: #000000;
          border: none;
          padding: 12px 24px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          border-radius: 8px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          white-space: nowrap;
        }

        .fire-btn:hover {
          background: #f0f0f0;
          transform: translateY(-2px);
        }

        .fire-btn:active {
          transform: translateY(0);
        }
      `}</style>
    </div>
  );
}