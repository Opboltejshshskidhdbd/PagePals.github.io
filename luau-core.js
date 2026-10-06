// Luau validator core: lexer + recursive-descent parser + scope analysis + Roblox checks.
// Works in browsers (ES module), Cloudflare Workers and Node.
const KW=new Set("and break do else elseif end false for function if in local nil not or repeat return then true until while".split(" "));
const GLOBALS=new Set("assert error getmetatable setmetatable ipairs pairs next pcall xpcall select tonumber tostring type typeof print warn rawequal rawget rawset rawlen require unpack newproxy collectgarbage gcinfo tick time wait spawn delay elapsedTime loadstring getfenv setfenv os math string table coroutine utf8 bit32 debug buffer task game workspace Workspace script plugin shared settings stats UserSettings version _G _VERSION Enum Instance Vector2 Vector3 Vector2int16 Vector3int16 Region3 Region3int16 CFrame Color3 BrickColor UDim UDim2 Rect Ray TweenInfo NumberRange NumberSequence NumberSequenceKeypoint ColorSequence ColorSequenceKeypoint Random DateTime Axes Faces Font OverlapParams RaycastParams PathWaypoint PhysicalProperties CatalogSearchParams DockWidgetPluginGuiInfo SharedTable FloatCurveKey RotationCurveKey".split(" "));
const SERVICES=new Set("Workspace Players Lighting ReplicatedStorage ReplicatedFirst ServerStorage ServerScriptService StarterGui StarterPack StarterPlayer Teams SoundService Chat TextChatService RunService UserInputService ContextActionService TweenService HttpService MarketplaceService DataStoreService MessagingService TeleportService CollectionService PhysicsService PathfindingService Debris GuiService TextService BadgeService GroupService LocalizationService VRService ProximityPromptService MemoryStoreService ContentProvider HapticService SocialService PolicyService AnalyticsService Stats".split(" "));
const CLASSES=new Set("Part MeshPart WedgePart CornerWedgePart TrussPart SpawnLocation Model Folder Tool Accessory Humanoid Script LocalScript ModuleScript RemoteEvent RemoteFunction BindableEvent BindableFunction StringValue IntValue NumberValue BoolValue ObjectValue Vector3Value CFrameValue Color3Value BrickColorValue Attachment Weld WeldConstraint Motor6D HingeConstraint SpringConstraint RopeConstraint AlignPosition AlignOrientation LinearVelocity AngularVelocity BodyVelocity BodyGyro BodyPosition BodyForce Sound SoundGroup ParticleEmitter Beam Trail Fire Smoke Sparkles Explosion PointLight SpotLight SurfaceLight Highlight Decal Texture SurfaceGui ScreenGui BillboardGui Frame TextLabel TextButton TextBox ImageLabel ImageButton ScrollingFrame ViewportFrame UICorner UIStroke UIListLayout UIGridLayout UIPadding UIScale UIGradient UIAspectRatioConstraint Animation Animator AnimationController Camera ClickDetector ProximityPrompt Seat VehicleSeat Configuration Shirt Pants ShirtGraphic ForceField Team Atmosphere Sky BlurEffect ColorCorrectionEffect BloomEffect SunRaysEffect DepthOfFieldEffect".split(" "));
const YIELD=new Set(["wait","Wait","WaitForChild","sleep"]);
const COMP=new Set(["+=","-=","*=","/=","//=","%=","^=","..="]);
const BIN={or:[1,1],and:[2,2],"<":[3,3],">":[3,3],"<=":[3,3],">=":[3,3],"~=":[3,3],"==":[3,3],"..":[5,4],"+":[6,6],"-":[6,6],"*":[7,7],"/":[7,7],"//":[7,7],"%":[7,7],"^":[10,9]};

export function lex(s){
  const T=[],E=[],n=s.length,out=[];let i=0,line=1,ls=0;
  const blank=(a,b)=>{for(let k=a;k<b;k++){if(s[k]==="\n"){line++;ls=k+1;out.push("\n")}else out.push(" ")}};
  const long=p=>{const m=/^\[(=*)\[/.exec(s.slice(p,p+50));if(!m)return -1;const c="]"+m[1]+"]",e=s.indexOf(c,p+m[0].length);return e<0?-2:e+c.length};
  const two=new Set(["==","~=","<=",">=","..","//","+=","-=","*=","/=","%=","^=","::","->"]);
  while(i<n){
    const ch=s[i],col=i-ls+1,ln=line;
    if(ch==="\n"){line++;ls=i+1;out.push(ch);i++;continue}
    if(/\s/.test(ch)){out.push(ch);i++;continue}
    if(ch==="-"&&s[i+1]==="-"){
      let e=long(i+2);
      if(e===-2){E.push({line:ln,col,rule:"syntax",severity:"error",message:"Unclosed long comment"});e=n}
      else if(e<0){e=s.indexOf("\n",i);if(e<0)e=n}
      blank(i,e);i=e;continue}
    if(ch==='"'||ch==="'"||ch==="`"){
      let k=i+1,ok=false;
      while(k<n){const d=s[k];if(d==="\\"){k+=2;continue}if(d===ch){ok=true;break}if(d==="\n"&&ch!=="`")break;k++}
      if(!ok)E.push({line:ln,col,rule:"syntax",severity:"error",message:"Unclosed string"});
      const e=ok?k+1:Math.min(k,n);
      T.push({t:"str",v:s.slice(i+1,ok?e-1:e),raw:s.slice(i,e),line:ln,col});blank(i,e);i=e;continue}
    if(ch==="["){
      const e=long(i);
      if(e===-2){E.push({line:ln,col,rule:"syntax",severity:"error",message:"Unclosed long string"});blank(i,n);i=n;continue}
      if(e>0){T.push({t:"str",v:"",raw:"[[",line:ln,col});blank(i,e);i=e;continue}}
    if(/\d/.test(ch)||(ch==="."&&/\d/.test(s[i+1]||""))){
      const m=/^(0[xX][\da-fA-F_]+|0[bB][01_]+|(\d[\d_]*)?\.?\d[\d_]*([eE][+-]?\d+)?)/.exec(s.slice(i,i+60));
      const v=m?m[0]:ch;T.push({t:"num",v,line:ln,col});out.push(v);i+=v.length;continue}
    if(/[A-Za-z_]/.test(ch)){
      const v=/^\w+/.exec(s.slice(i,i+200))[0];
      T.push({t:KW.has(v)?"kw":"id",v,line:ln,col});out.push(v);i+=v.length;continue}
    let v=ch;
    const t3=s.substr(i,3);
    if(t3==="..."||t3==="..="||t3==="//=")v=t3;else if(two.has(s.substr(i,2)))v=s.substr(i,2);
    if(v.length===1&&"$!\\".includes(v))E.push({line:ln,col,rule:"syntax",severity:"error",message:`Unexpected character '${v}'`});
    T.push({t:"sym",v,line:ln,col});out.push(v);i+=v.length;
  }
  T.push({t:"eof",v:"<eof>",line,col:i-ls+1});
  return{T,E,clean:out.join("")};
}

class PErr{constructor(t,m){this.t=t;this.m=m}}

export function validate(src,rules=[]){
  const{T,E,clean}=lex(src);
  const errors=[...E],warnings=[];
  const stats={lines:src.split("\n").length,tokens:T.length-1,functions:0,locals:0,maxDepth:0};
  let p=0,sc=[new Map()],fn={vararg:true,loops:0},depth=0,yields=0,sawExit=false;
  const at=(t,rule,message,severity)=>({line:t.line,col:t.col,rule,severity,message});
  const pk=(o=0)=>T[Math.min(p+o,T.length-1)];
  const nx=()=>{const t=T[p];if(t.t!=="eof")p++;return t};
  const is=v=>{const t=pk();return(t.t==="kw"||t.t==="sym")&&t.v===v};
  const eat=v=>is(v)?nx():null;
  const desc=t=>t.t==="eof"?"end of file":`'${t.t==="str"?t.raw:t.v}'`;
  const fail=(m,t=pk())=>{throw new PErr(t,m)};
  const need=(v,open)=>{if(is(v))return nx();fail(`Expected '${v}'${open?` (to close '${open.v}' from line ${open.line})`:""}, got ${desc(pk())}`)};
  const nameTok=()=>{const t=pk();if(t.t!=="id")fail(`Expected a name, got ${desc(t)}`);return nx()};
  const find=n=>{for(let i=sc.length-1;i>=0;i--)if(sc[i].has(n))return sc[i].get(n);return null};
  const flush=m=>{for(const[n,v]of m)if(!v.used&&!v.param&&n[0]!=="_")warnings.push(at(v.tok,"unused-local",`Local '${n}' declare hua par kabhi read nahi hua`,"info"))};
  const push=()=>{sc.push(new Map());depth++;stats.maxDepth=Math.max(stats.maxDepth,depth)};
  const pop=()=>{flush(sc.pop());depth--};
  const declare=(t,o={})=>{
    if(!o.param&&t.v!=="_"){const e=find(t.v);if(e)warnings.push(at(t,"shadow",`'${t.v}' shadow ho raha hai (pehle line ${e.tok.line} par declare)`,"info"))}
    sc[sc.length-1].set(t.v,{tok:t,used:false,...o});stats.locals++};
  const use=t=>{const v=find(t.v);if(v){v.used=true;return}if(!GLOBALS.has(t.v))warnings.push(at(t,"undefined-global",`'${t.v}' define nahi hai (undefined global)`,"warning"))};
  const assign=t=>{if(!find(t.v)&&!GLOBALS.has(t.v))warnings.push(at(t,"global-assign",`'${t.v}' global ban raha hai — 'local' lagana tha?`,"warning"))};

  // ---- types (parsed and skipped) ----
  const skipBal=(o,c)=>{let d=0;do{const t=nx();if(t.t==="eof")fail("Unclosed type expression",t);if(t.t==="sym"){if(t.v===o)d++;else if(t.v===c)d--}}while(d>0)};
  const skipType=()=>{
    const one=()=>{const t=pk();
      if(is("(")){skipBal("(",")");if(is("->")){nx();skipType()}}
      else if(is("{"))skipBal("{","}");
      else if(is("...")){nx();skipType()}
      else if(t.t==="id"){nx();if(t.v==="typeof"&&is("("))skipBal("(",")");else{while(is(".")){nx();nameTok()}if(is("<"))skipBal("<",">")}}
      else if(t.t==="str"||(t.t==="kw"&&["nil","true","false"].includes(t.v)))nx();
      else fail(`Type expected, got ${desc(t)}`)};
    one();while(is("|")||is("&")||is("?")){const o=nx();if(o.v!=="?")one()}};

  // ---- expressions ----
  const interp=t=>{for(const m of t.raw.matchAll(/\{([^{}]*)\}/g))for(const id of m[1].matchAll(/(?<![.\w])[A-Za-z_]\w*/g))if(!KW.has(id[0]))use({v:id[0],line:t.line,col:t.col})};
  const args=()=>{let s=null;
    if(is("(")){nx();const a=pk(),b=pk(1);if(a.t==="str"&&(b.v===")"||b.v===","))s=a;if(!is(")")){expr();while(eat(","))expr()}need(")")}
    else if(pk().t==="str")s=nx();
    else table();
    return s};
  const onCall=(path,s)=>{
    if(YIELD.has(path.split(/[.:]/).pop()))yields++;
    if(s&&s.raw[0]!=="`"){
      if(path.endsWith(":GetService")&&!SERVICES.has(s.v))warnings.push(at(s,"unknown-service",`'${s.v}' known Roblox service nahi lagta (spelling?)`,"warning"));
      if(path==="Instance.new"&&!CLASSES.has(s.v))warnings.push(at(s,"unknown-class",`Instance.new('${s.v}') — class name check karo`,"info"))}};
  const suffixed=()=>{
    let k="exp",path="",t=pk();
    if(t.t==="id"){nx();use(t);k="name";path=t.v}
    else if(is("(")){nx();expr();need(")")}
    else fail(`Unexpected ${desc(t)}`);
    for(;;){
      if(is(".")){nx();path+="."+nameTok().v;k="index"}
      else if(is("[")){nx();expr();need("]");path="";k="index"}
      else if(is(":")){nx();path+=":"+nameTok().v;const s=args();onCall(path,s);path="";k="call"}
      else if(is("(")||pk().t==="str"||is("{")){const s=args();onCall(path,s);path="";k="call"}
      else break}
    return k};
  const table=()=>{
    need("{");
    while(!is("}")){
      if(is("[")){nx();expr();need("]");need("=");expr()}
      else if(pk().t==="id"&&pk(1).v==="="&&pk(1).t==="sym"){nx();nx();expr()}
      else expr();
      if(!eat(",")&&!eat(";"))break}
    need("}")};
  const ifexpr=()=>{nx();expr();need("then");expr();while(is("elseif")){nx();expr();need("then");expr()}need("else");expr()};
  const simple=()=>{
    const t=pk();
    if(t.t==="num")nx();
    else if(t.t==="str"){nx();if(t.raw[0]==="`")interp(t)}
    else if(t.t==="kw"&&(t.v==="nil"||t.v==="true"||t.v==="false"))nx();
    else if(is("...")){if(!fn.vararg)fail("'...' sirf vararg function me allowed hai");nx()}
    else if(is("{"))table();
    else if(is("function")){const f=nx();funcbody(f,false)}
    else if(is("if"))ifexpr();
    else suffixed();
    while(is("::")){nx();skipType()}};
  const expr=(lim=0)=>{
    const t=pk();
    if((t.t==="kw"&&t.v==="not")||(t.t==="sym"&&(t.v==="-"||t.v==="#"))){nx();expr(8)}else simple();
    for(;;){const o=pk(),b=(o.t==="kw"||o.t==="sym")&&BIN[o.v];if(!b||b[0]<=lim)break;nx();expr(b[1])}};
  const exprlist=()=>{expr();while(eat(","))expr()};

  // ---- functions & statements ----
  const funcbody=(open,self)=>{
    stats.functions++;
    if(is("<"))skipBal("<",">");
    need("(");
    const saved=fn;fn={vararg:false,loops:0};push();
    if(self)declare({v:"self",line:open.line,col:open.col},{used:true,param:true});
    const seen=new Set();
    if(!is(")")){do{
      if(is("...")){nx();fn.vararg=true;if(eat(":"))skipType();break}
      const t=nameTok();
      if(seen.has(t.v))errors.push(at(t,"duplicate-param",`Duplicate parameter '${t.v}'`,"error"));
      seen.add(t.v);declare(t,{param:true});
      if(eat(":"))skipType();
    }while(eat(","))}
    need(")");
    if(eat(":"))skipType();
    block(["end"]);need("end",open);pop();fn=saved};
  const block=terms=>{
    for(;;){
      const t=pk();
      if(t.t==="eof"||(t.t==="kw"&&terms.includes(t.v)))return;
      if(t.t==="kw"&&t.v==="return"){
        nx();sawExit=true;
        const n=pk();
        if(!(n.t==="eof"||(n.t==="kw"&&["end","else","elseif","until"].includes(n.v))||is(";")))exprlist();
        eat(";");
        const m=pk();
        if(!(m.t==="eof"||(m.t==="kw"&&terms.includes(m.v))))fail("'return' block ka last statement hona chahiye",m);
        return}
      stat()}};
  const loopBody=(t,inf,decl)=>{
    fn.loops++;push();if(decl)decl();
    const y=yields,e=sawExit;sawExit=false;
    block(["end"]);need("end",t);pop();fn.loops--;
    if(inf&&yields===y&&!sawExit)warnings.push(at(t,"infinite-loop","'while true' me yield (task.wait) nahi hai — script freeze/timeout ho sakti hai","warning"));
    sawExit=e||sawExit};
  const typedecl=()=>{if(pk().v==="export")nx();nx();nameTok();if(is("<"))skipBal("<",">");need("=");skipType()};
  const localstat=()=>{
    nx();
    if(is("function")){nx();const n=nameTok();declare(n);funcbody({v:"function",line:n.line,col:n.col},false);return}
    const names=[];
    do{const n=nameTok();if(eat(":"))skipType();names.push(n)}while(eat(","));
    if(eat("="))exprlist();
    names.forEach(n=>declare(n))};
  const forstat=t=>{
    nx();const n1=nameTok();
    if(is("=")){nx();expr();need(",");expr();if(eat(","))expr();need("do");loopBody(t,false,()=>declare(n1,{param:true}))}
    else{
      const names=[n1];while(eat(","))names.push(nameTok());
      need("in");exprlist();need("do");
      loopBody(t,false,()=>names.forEach(n=>declare(n,{param:true})))}};
  const exprstat=()=>{
    const t=pk();
    const isAsgn=x=>x.t==="sym"&&(x.v==="="||x.v===","||COMP.has(x.v));
    const tgt=()=>{const a=pk(),b=pk(1);if(a.t==="id"&&isAsgn(b)){nx();return{k:"name",t:a}}return{k:suffixed()}};
    const f=tgt();
    if(f.k==="call"&&!isAsgn(pk()))return;
    if(f.k!=="name"&&!isAsgn(pk()))fail("Ye expression statement nahi ho sakta (sirf function call allowed hai)",t);
    const ts=[f];while(eat(","))ts.push(tgt());
    for(const x of ts)if(x.k!=="name"&&x.k!=="index")fail("Invalid assignment target",t);
    if(COMP.has(pk().v)&&pk().t==="sym"){nx();expr();for(const x of ts)if(x.k==="name")use(x.t);return}
    need("=");exprlist();
    for(const x of ts)if(x.k==="name")assign(x.t)};
  const stat=()=>{
    const t=pk();
    if(is(";")){nx();return}
    if(t.t==="kw"){
      switch(t.v){
        case"local":return localstat();
        case"function":{
          nx();const n=nameTok();let m=false;
          while(is(".")){nx();nameTok()}
          if(is(":")){nx();nameTok();m=true}
          return funcbody({v:"function",line:t.line,col:t.col},m)}
        case"if":{
          nx();expr();need("then");push();block(["elseif","else","end"]);pop();
          while(is("elseif")){nx();expr();need("then");push();block(["elseif","else","end"]);pop()}
          if(eat("else")){push();block(["end"]);pop()}
          need("end",t);return}
        case"while":{nx();const inf=pk().v==="true"&&pk(1).v==="do";expr();need("do");return loopBody(t,inf)}
        case"for":return forstat(t);
        case"repeat":{nx();fn.loops++;push();block(["until"]);need("until",t);expr();pop();fn.loops--;return}
        case"do":{nx();push();block(["end"]);need("end",t);pop();return}
        case"break":nx();if(!fn.loops)fail("'break' loop ke bahar hai",t);sawExit=true;return;
        default:fail(`Unexpected '${t.v}' (extra 'end' ya missing opener?)`)}}
    if(t.t==="id"){
      if(t.v==="continue"&&!["=","(",".",":","[",","].includes(pk(1).v)){nx();if(!fn.loops)fail("'continue' loop ke bahar hai",t);return}
      if(t.v==="export"&&pk(1).v==="type"){typedecl();return}
      if(t.v==="type"&&pk(1).t==="id"&&(pk(2).v==="="||pk(2).v==="<")){typedecl();return}}
    exprstat()};

  let parsed=false;
  try{block([]);if(pk().t!=="eof")fail(`Unexpected ${desc(pk())}`);parsed=true}
  catch(e){if(!(e instanceof PErr))throw e;errors.push(at(e.t,"syntax",e.m,"error"))}
  if(parsed)flush(sc[0]);

  for(const r of rules){
    let re;try{re=new RegExp(r.regex,"g")}catch{continue}
    let m;
    while((m=re.exec(clean))){
      const pre=clean.slice(0,m.index),line=pre.split("\n").length,col=m.index-pre.lastIndexOf("\n");
      (r.severity==="error"?errors:warnings).push({line,col,rule:r.id,severity:r.severity,message:r.message});
      if(m[0]==="")re.lastIndex++}}
  const by=(a,b)=>a.line-b.line||(a.col||0)-(b.col||0);
  errors.sort(by);warnings.sort(by);
  return{valid:errors.length===0,errors,warnings,stats};
}
