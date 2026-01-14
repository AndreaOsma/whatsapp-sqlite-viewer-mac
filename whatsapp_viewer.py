import sqlite3
import os
from datetime import datetime

# Offset de tiempo para bases de datos de WhatsApp (Apple Epoch)
OFFSET = 978307200 

def generate_html():
    db_file = 'ChatStorage.sqlite'
    if not os.path.exists(db_file):
        print(f"Error: No se encuentra el archivo {db_file}")
        return
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Mapeo de sesiones de chat
    cursor.execute("SELECT Z_PK, ZPARTNERNAME FROM ZWACHATSESSION")
    chat_names = {row[0]: (row[1] if row[1] else f"Chat {row[0]}") for row in cursor.fetchall()}
    
    # Obtención de estadísticas por volumen de mensajes
    cursor.execute("SELECT ZCHATSESSION, COUNT(*) FROM ZWAMESSAGE GROUP BY ZCHATSESSION ORDER BY COUNT(*) DESC")
    chat_stats = cursor.fetchall()

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write('''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>WhatsApp Archive Viewer</title>
            <style>
                :root { 
                    --bg: #0b141a; --side: #111b21; --header: #202c33; 
                    --msg-in: #202c33; --msg-out: #005c4b; --text: #e9edef; 
                    --accent: #00a884; --sub: #8696a0; --border: #2f3b44;
                }
                .light-mode {
                    --bg: #efeae2; --side: #ffffff; --header: #f0f2f5; 
                    --msg-in: #ffffff; --msg-out: #d9fdd3; --text: #111b21; 
                    --accent: #008069; --sub: #667781; --border: #d1d7db;
                }
                body { font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; height: 100vh; background: var(--bg); color: var(--text); overflow: hidden; }
                #sidebar { width: 350px; background: var(--side); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
                .chat-list { overflow-y: auto; flex: 1; }
                .chat-item { padding: 15px; border-bottom: 1px solid var(--border); cursor: pointer; }
                .chat-item.active { background: rgba(0,168,132,0.15); border-left: 4px solid var(--accent); }
                #main { flex: 1; display: flex; flex-direction: column; position: relative; background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'); background-blend-mode: overlay; background-color: var(--bg); }
                header { background: var(--header); padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }
                .conv-container { flex: 1; overflow-y: auto; padding: 20px 8%; display: flex; flex-direction: column; scroll-behavior: smooth; }
                .msg { margin-bottom: 8px; padding: 8px 12px; border-radius: 8px; max-width: 70%; font-size: 14.2px; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13); }
                .me { background: var(--msg-out); align-self: flex-end; border-top-right-radius: 0; }
                .them { background: var(--msg-in); align-self: flex-start; border-top-left-radius: 0; }
                .date-sep { text-align: center; margin: 20px 0; font-size: 11px; color: var(--sub); }
                .time { font-size: 10px; color: var(--sub); text-align: right; margin-top: 4px; }
                #btn-bottom { position: absolute; bottom: 25px; right: 25px; width: 45px; height: 45px; border-radius: 50%; background: var(--header); color: var(--text); border: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 1000; }
                .hidden { display: none; }
            </style>
        </head>
        <body>
            <div id="sidebar">
                <div style="padding:20px; font-weight:bold; color:var(--accent); font-size:1.3em;">WA Viewer</div>
                <div style="padding:10px;"><input type="text" id="chatSearch" placeholder="Buscar..." onkeyup="filter()" style="width:90%; padding:8px; background:var(--bg); color:var(--text); border:1px solid var(--border); border-radius:5px;"></div>
                <div class="chat-list">
        ''')

        for cid, count in chat_stats:
            name = chat_names.get(cid, f"Chat {cid}")
            f.write(f'<div class="chat-item" id="item-{cid}" onclick="openChat({cid}, \'{name}\')"><b>{name}</b><br><small style="color:var(--sub)">{count} mensajes</small></div>')
        
        f.write('</div></div><div id="main"><header><span id="chat-name">Selecciona un chat</span><button onclick="toggleTheme()" style="cursor:pointer; background:var(--accent); color:white; border:none; padding:5px 10px; border-radius:5px;">Tema</button></header>')
        f.write('<button id="btn-bottom" onclick="scrollToBottom()">▼</button>')

        for cid, count in chat_stats:
            f.write(f'<div id="conv-{cid}" class="conv-container hidden">')
            cursor.execute("""
                SELECT m.ZTEXT, m.ZMESSAGEDATE, m.ZISFROMME, mi.ZMEDIALOCALPATH 
                FROM ZWAMESSAGE m 
                LEFT JOIN ZWAMEDIAITEM mi ON m.Z_PK = mi.ZMESSAGE 
                WHERE m.ZCHATSESSION = ? 
                ORDER BY m.ZMESSAGEDATE ASC
            """, (cid,))
            
            last_date = ""
            for text, ts, is_me, mpath in cursor.fetchall():
                try:
                    dt = datetime.fromtimestamp(ts + OFFSET)
                    d_str = dt.strftime('%d %b %Y')
                    t_str = dt.strftime('%H:%M')
                    if d_str != last_date:
                        f.write(f'<div class="date-sep">{d_str}</div>')
                        last_date = d_str
                except: t_str = ""

                side = "me" if is_me == 1 else "them"
                f.write(f'<div class="msg {side}">')
                if text: f.write(f'<div>{text}</div>')
                if mpath:
                    # Normalización de ruta para visualización local
                    p = mpath.replace('Message/Media/', 'Media/')
                    if not p.startswith('Media/'): p = 'Media/' + p
                    if p.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        f.write(f'<div style="margin-top:5px;"><img src="{p}" style="max-width:100%; border-radius:5px;" loading="lazy"></div>')
                f.write(f'<div class="time">{t_str}</div></div>')
            f.write('</div>')
        f.write('''
            </div>
            <script>
                function toggleTheme() { document.body.classList.toggle('light-mode'); }
                function scrollToBottom() { const activeConv = document.querySelector('.conv-container:not(.hidden)'); if (activeConv) activeConv.scrollTop = activeConv.scrollHeight; }
                function openChat(id, name) {
                    document.querySelectorAll('.conv-container').forEach(c => c.classList.add('hidden'));
                    document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
                    const chat = document.getElementById('conv-'+id);
                    chat.classList.remove('hidden');
                    document.getElementById('item-'+id).classList.add('active');
                    document.getElementById('chat-name').innerText = name;
                    setTimeout(() => { chat.scrollTop = chat.scrollHeight; }, 50);
                }
                function filter(){ 
                    let v = document.getElementById("chatSearch").value.toLowerCase(); 
                    document.querySelectorAll(".chat-item").forEach(i => { i.style.display = i.innerText.toLowerCase().includes(v) ? "" : "none" }); 
                }
            </script>
        </body>
        </html>''')
    
    conn.close()
    print("Finalizado: index.html generado con éxito.")

if __name__ == "__main__":
    generate_html()

