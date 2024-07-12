import React, { useEffect, useRef, useState } from 'react';
import styles from "./chat.module.css";
import { Message } from "@/lib/Messages";
import SendMessage from "@/lib/SendMessage";
import Typing from "./Typing";

export default function Chat(props: any) {
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const chatWindowRef = useRef<HTMLDivElement>(null);

  const handleMessageSend = async () => {
    const new_message = inputValue;
    setInputValue(''); // Clear input field
    setLoading(true);
    const userMessage = new Message();
    userMessage.text = new_message;
    userMessage.type = "user";
    props.addMessage(userMessage);
    setLoading(true);
    try {
      const response = await SendMessage(props.videoURL, new_message);
      const botMessage = new Message();
      botMessage.text = response.generated_text;
      botMessage.type = "bot";
      setLoading(false);
      props.addMessage(botMessage);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [props.messages]);

  return (
    <div className={styles.chatdiv}>
      {/* <h4>Chat</h4> */}
      <div ref={chatWindowRef} className={styles.chatwindow}>
        <div style={{"height":"95%"}}>
        {props.messages.map((element: Message, index: number) => (
          <p className={element.type} key={index}>{element.text}</p>
        ))}
        </div>
      
      {loading ? <div className='loading-div'><Typing /></div>: ""}
      </div>
      
      <div className={styles.inputbar}>
        <input
          type="text"
          className="form-control"
          placeholder="Type your message here..."
          aria-label="User message"
          aria-describedby="button-addon2"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleMessageSend();
            }
          }}
          id="user_message"
        />
        <button
          className="btn btn-outline-secondary"
          type="button"
          id="button-addon2"
          onClick={handleMessageSend}
          disabled={loading}
        >
          <i className="bi bi-send"></i>
        </button>
      </div>
    </div>
  );
}
