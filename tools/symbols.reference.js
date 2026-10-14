/* hand-drawn symbols, returned as ordered pen strokes (in writing order) */
const SYM_ZH={heart:'愛心',star:'星星',sparkle:'閃亮星芒',smile:'笑臉',wink:'眨眼笑臉',laugh:'大笑臉',note:'音符',sun:'太陽',moon:'月亮',flower:'小花',crown:'皇冠',infinity:'無限符號',bolt:'閃電',check:'勾勾',wave:'波浪',plus:'加號'};
function doodle(type,cx,cy,s){
  const out=[],R=s/2;
  const arc=(x,y,r,a0,a1,n=40,sy=1)=>{const a=[];for(let i=0;i<=n;i++){const g=a0+(a1-a0)*i/n;a.push([x+Math.cos(g)*r,y+Math.sin(g)*r*sy])}return a};
  const dot=(x,y,e)=>[[x,y-e*.5],[x+e*.3,y],[x,y+e*.5],[x-e*.3,y],[x,y-e*.5]];
  const face=(kind,withOutline)=>{
    if(withOutline)out.push({pts:arc(cx,cy,R,-Math.PI*.35,-Math.PI*2.4,44),name:'臉的輪廓'});
    const e=s*.13,ey=cy-s*.1,lx=cx-s*.17,rx=cx+s*.17,hat=(x)=>[[x-s*.09,ey+e*.25],[x,ey-e*.45],[x+s*.09,ey+e*.25]];
    if(kind==='laugh'){out.push({pts:hat(lx),name:'左眼'});out.push({pts:hat(rx),name:'右眼'});
      const m=[[cx-s*.24,cy+s*.06],...arc(cx,cy+s*.06,s*.24,Math.PI,0,18).reverse().map(p=>[p[0],cy+s*.06+(cy+s*.06-p[1])*-.9]),[cx-s*.24,cy+s*.06]];out.push({pts:m,name:'張口大笑'})}
    else{out.push({pts:dot(lx,ey,e),name:'左眼'});out.push({pts:kind==='wink'?hat(rx):dot(rx,ey,e),name:kind==='wink'?'眨眼':'右眼'});
      out.push({pts:arc(cx,cy+s*.02,s*.26,Math.PI*.85,Math.PI*.15,16,.85),name:'微笑嘴巴'})}};
  switch(type){
    case'heart':{const a=[];for(let i=0;i<=44;i++){const t=Math.PI*2*i/44,x=16*Math.pow(Math.sin(t),3),y=13*Math.cos(t)-5*Math.cos(2*t)-2*Math.cos(3*t)-Math.cos(4*t);a.push([cx+x*s/34,cy-(y+2.5)*s/34])}out.push({pts:a,name:'愛心'});break}
    case'star':{const a=[];for(let k=0;k<=5;k++){const g=-Math.PI/2+k*Math.PI*.8;a.push([cx+Math.cos(g)*R,cy+Math.sin(g)*R])}out.push({pts:a,name:'星星'});break}
    case'sparkle':{const a=[];for(let i=0;i<=48;i++){const g=-Math.PI/2+i/48*Math.PI*2,rr=R*(.3+.7*Math.pow(Math.abs(Math.cos(2*g)),1.8));a.push([cx+Math.cos(g)*rr,cy+Math.sin(g)*rr])}out.push({pts:a,name:'閃亮星芒'});break}
    case'smile':case'wink':case'laugh':face(type,true);break;
    case'eyes:smile':face('smile',false);break;case'eyes:wink':face('wink',false);break;case'eyes:laugh':face('laugh',false);break;
    case'note':{out.push({pts:arc(cx-s*.14,cy+s*.28,s*.15,-.4,-.4-Math.PI*2.05,28,.72),name:'音符的符頭'});
      out.push({pts:[[cx+.01*s,cy+s*.25],[cx+.01*s,cy-s*.45],...bez([cx+.01*s,cy-s*.45],[cx+s*.1,cy-s*.3],[cx+s*.32,cy-s*.25],[cx+s*.26,cy-s*.02],10)],name:'符桿與符尾'});break}
    case'sun':{out.push({pts:arc(cx,cy,s*.24,-Math.PI/2,-Math.PI/2-Math.PI*2.02,34),name:'太陽'});
      const a=[];for(let i=0;i<=16;i++){const g=-Math.PI/2+i/16*Math.PI*2,rr=i%2?s*.34:s*.5;a.push([cx+Math.cos(g)*rr,cy+Math.sin(g)*rr])}out.push({pts:a,name:'光芒'});break}
    case'moon':{const a=arc(cx,cy,R,-Math.PI*.4,-Math.PI*1.6,30),b=arc(cx+R*.4,cy,R*.78,Math.PI*.58,Math.PI*1.42,26);out.push({pts:[...a,...b.slice(1),a[0]],name:'月亮'});break}
    case'flower':{const a=[];for(let i=0;i<=120;i++){const g=i/120*Math.PI*2,rr=R*Math.abs(Math.cos(2.5*g));a.push([cx+Math.cos(g-Math.PI/2)*rr,cy+Math.sin(g-Math.PI/2)*rr])}out.push({pts:a,name:'花瓣'});out.push({pts:dot(cx,cy,s*.14),name:'花心'});break}
    case'crown':{const w=s,h=s*.62;out.push({pts:[[cx-w/2,cy+h/2],[cx-w/2,cy-h/2],[cx-w/4,cy+h*.05],[cx,cy-h*.62],[cx+w/4,cy+h*.05],[cx+w/2,cy-h/2],[cx+w/2,cy+h/2],[cx-w/2,cy+h/2]],name:'皇冠'});break}
    case'infinity':{const a=[];for(let i=0;i<=60;i++){const t=i/60*Math.PI*2,d=1+Math.sin(t)**2;a.push([cx+R*1.1*Math.cos(t)/d,cy+R*1.1*Math.sin(t)*Math.cos(t)/d])}out.push({pts:a,name:'無限符號'});break}
    case'bolt':out.push({pts:[[cx+s*.12,cy-R],[cx-s*.2,cy+s*.05],[cx+s*.08,cy+s*.05],[cx-s*.14,cy+R]],name:'閃電'});break;
    case'check':out.push({pts:[[cx-R*.8,cy],[cx-R*.2,cy+R*.6],[cx+R*.9,cy-R*.7]],name:'勾勾'});break;
    case'wave':{const a=[];for(let i=0;i<=40;i++){const u=i/40;a.push([cx-R+u*s,cy+Math.sin(u*Math.PI*3)*s*.14])}out.push({pts:a,name:'波浪'});break}
    case'plus':out.push({pts:[[cx-R*.6,cy],[cx+R*.6,cy]],name:'加號橫'});out.push({pts:[[cx,cy-R*.6],[cx,cy+R*.6]],name:'加號直'});break;
    default:return doodle('star',cx,cy,s);
  }
  return out}
// symbols typed inside a name: emoji, dingbats and text emoticons
const SYM_MAP=[['^_^','laugh'],[':-)','smile'],['<3','heart'],[':)','smile'],[';)','wink'],[':D','laugh'],['^^','laugh'],['♡','heart'],['♥','heart'],['❤','heart'],['💕','heart'],['💖','heart'],['💗','heart'],['😍','heart'],['☆','star'],['★','star'],['⭐','star'],['🌟','sparkle'],['✦','sparkle'],['✧','sparkle'],['✨','sparkle'],['☺','smile'],['😊','smile'],['🙂','smile'],['😀','laugh'],['😄','laugh'],['😆','laugh'],['😁','laugh'],['😉','wink'],['😜','wink'],['♪','note'],['♫','note'],['🎵','note'],['🎶','note'],['☀','sun'],['🌞','sun'],['☾','moon'],['🌙','moon'],['✿','flower'],['❀','flower'],['🌸','flower'],['🌼','flower'],['👑','crown'],['♛','crown'],['∞','infinity'],['⚡','bolt'],['✓','check'],['✔','check'],['～','wave'],['~','wave'],['+','plus']];
function tokenize(s){
  const out=[];let i=0;
  while(i<s.length){
    const m=SYM_MAP.find(([k])=>s.startsWith(k,i));
    if(m){out.push({t:'sym',v:m[1],raw:m[0]});i+=m[0].length;if(s[i]==='️')i++;continue}
    const cp=s.codePointAt(i),ch=String.fromCodePoint(cp);i+=ch.length;
    if(ch==='️'||ch==='‍')continue;
    if(/\s/.test(ch))out.push({t:'sp'});
    else if(/[A-Za-z]/.test(ch))out.push({t:'L',c:ch});
    else if(/[0-9]/.test(ch))out.push({t:'D',c:ch});
    else if(isCJK(ch))out.push({t:'C',c:ch});
    else if(/[.\-_'!?&,]/.test(ch))out.push({t:'P',c:ch});
    else if(/\p{Extended_Pictographic}/u.test(ch))out.push({t:'sym',v:'sparkle',raw:ch,unknown:true});
    else out.push({t:'X',c:ch});
  }
  return out}
