import json, random, re, pathlib, collections
random.seed(2207)
root=pathlib.Path(__file__).resolve().parent
questions=[]
cats=[
('agreement','主語と動詞','文法','主語が三人称単数なら現在形に -s / -es。every day は現在形の目印。'),
('tense','時制','文法','yesterday / last ～ は過去形、now は進行形、tomorrow は未来を考える。'),
('perfect','現在完了','文法','have/has + 過去分詞。since は起点、for は期間。'),
('modal','助動詞','文法','助動詞の直後は動詞の原形。must not は禁止、do not have to は不要。'),
('passive','受動態','文法','be動詞 + 過去分詞で「～される」。主語が動作を受けるか判断する。'),
('gerund','不定詞・動名詞','文法','want to do、enjoy doing、look forward to doing など動詞ごとの型を覚える。'),
('comparison','比較','文法','than は比較級、the ～ in/of は最上級、as ～ as は原級。'),
('relative','関係詞','文法','人を説明する who/that、物を説明する which/that、場所の where。'),
('preposition','前置詞','文法','at は時刻、on は曜日、in は月・年。by は期限、until は継続。'),
('conjunction','接続詞・条件','文法','if/when の条件・時を表す節では、未来のことでも現在形を使う。'),
('article','冠詞・名詞','文法','単数可算名詞には a/an/the 等が必要。information や advice は不可算。'),
('wordform','品詞・語順','文法','冠詞の後は名詞、名詞の前は形容詞、動詞を修飾するのは副詞。'),
('conditional','仮定法・応用','文法','現実と異なる仮定は If + 過去形、would + 原形など。'),
('vocab_general','基本語彙','語彙','一般教養の頻出語を、英文の文脈とともに覚える。'),
('vocab_business','仕事・IT語彙','語彙','仕事の連絡、予定、品質、IT業務に関する基本語彙。'),
('reading','短文・実務読解','読解','最初に設問を確認。本文中の日時・理由・目的・変更点に注目。'),
]
catnames={c[0]:c[1] for c in cats}

def add(cat, stem, answer, wrongs, explanation, level=1, passage=None):
    assert cat in catnames
    assert len(wrongs)==3 and len({answer,*wrongs})==4,(cat,stem,answer,wrongs)
    opts=[answer,*wrongs]; random.shuffle(opts)
    q={'id':f'q{len(questions)+1:04}', 'cat':cat,'level':level,'stem':stem,'choices':opts,'answer':opts.index(answer),'explanation':explanation}
    if passage: q['passage']=passage
    questions.append(q)

# Grammar rows format: stem | correct | distractor1 | distractor2 | distractor3 | explanation (one or two short sentences) | level
G={
'agreement': '''
The office ___ at nine every weekday.|opens|open|opening|opened|The office は三人称単数。現在の習慣は opens。|1
My colleagues ___ near Nagoya Station.|work|works|working|worked|My colleagues は複数なので現在形は work。|1
Everyone in the team ___ a laptop.|has|have|having|had|everyone は単数扱い。has を使う。|2
Neither answer ___ correct.|is|are|be|were|neither は通常単数扱いで is。|2
The number of users ___ increasing.|is|are|be|have|the number of ～ は単数主語。a number of と区別。|3
There ___ three files on the desk.|are|is|be|has|there are + 複数名詞。|1
Each employee ___ an ID card.|needs|need|needing|needed|each + 単数名詞は単数主語。|2
The manager and the engineer ___ in the room.|are|is|be|was|and で結ばれた2人は複数主語。|1
One of my friends ___ in Tokyo.|lives|live|living|are living|主語は one なので三人称単数。|2
The news ___ important.|is|are|were|have|news は語尾が -s でも単数扱い。|2
These devices ___ very reliable.|are|is|was|has|these + 複数名詞には are。|1
A list of tasks ___ on the wall.|is|are|be|have|主語の中心は a list（単数）。|2
Ten minutes ___ enough for this task.|is|are|were|have|時間・金額をまとまりとして扱うと単数。|3
The quality of these products ___ high.|is|are|were|have|主語は quality（単数）。|2
Both of the reports ___ ready.|are|is|has|be|both は複数扱い。|1
''',
 'tense': '''
We ___ the software yesterday.|updated|update|updating|updates|yesterday は過去の目印。updated。|1
She ___ an email right now.|is writing|writes|wrote|has written|right now は今進行中なので現在進行形。|1
They ___ the office last Friday.|visited|visit|visits|visiting|last Friday は過去なので visited。|1
I usually ___ the train to work.|take|took|am taking|taken|usually は現在の習慣。take。|1
Look! The screen ___ blue.|is turning|turns|turned|has turn|Look! は今の変化に注目。is turning。|2
The meeting ___ at 10 a.m. tomorrow.|starts|started|start|starting|確定した時刻表・予定は現在形で未来を表せる。|2
When I arrived, the meeting ___.|had already started|has already started|already starts|will already start|到着より前に始まっていたので過去完了。|3
He ___ dinner when I called.|was cooking|cooks|has cooked|will cook|電話したとき進行中だったので過去進行形。|2
My boss ___ to Osaka next week.|will travel|traveled|travel|travels yesterday|next week なので未来表現 will travel。|1
The train ___ before we reached the station.|had left|has left|leaves|will leave|過去の別の時点より前なので過去完了。|3
I ___ my keys this morning and found them later.|lost|lose|am losing|have lost|見つけた過去の出来事なので lost。|2
The students ___ for the test at the moment.|are studying|study yesterday|studied tomorrow|has studied|at the moment は今の進行を示す。|1
Last year, the company ___ a new branch.|opened|opens|is opening|will open|last year は過去。|1
We ___ a new server next month.|will install|installed|installs yesterday|installing|next month は未来。|1
He ___ home before the rain began.|had returned|has returned|will return|returns|雨の前に帰ったという過去の前後関係。|3
The sun ___ in the east.|rises|rose now|is rise|has rising|一般的な事実は現在形。|1
I ___ a call at 3 p.m. yesterday.|was taking|am taking|will take|have take|過去の特定時刻に進行中なら was taking。|2
We ___ the result by tomorrow.|will know|knew yesterday|knowing|known|by tomorrow は未来の期限。will know。|2
The lights ___ off when we entered.|were|are|will|has|entered が過去なので、その時の状態も were。|2
She ___ in Kyoto before moving to Nagoya.|lived|lives now|will live|living|moving の前の過去の居住。lived。|2
By the time we arrived, the store ___.|had closed|has closed|will close|closes|到着時までに閉まっていたので過去完了。|3
Listen! Someone ___ at the door.|is knocking|knocks yesterday|knocked tomorrow|has knock|Listen! は今起きている動作。|1
''',
'perfect': '''
We have worked here ___ 2022.|since|for|during|until|2022 は起点なので since。|1
She has studied English ___ three years.|for|since|at|by|three years は期間なので for。|1
I have ___ that movie twice.|seen|saw|see|seeing|have + 過去分詞 seen。|1
They have already ___ the report.|finished|finish|finishing|finishes|have + 過去分詞 finished。|1
Have you ___ been to Fukuoka?|ever|never|yet|still|経験を質問する have you ever been ～。|2
I haven't received the email ___.|yet|already|ever|just|否定文の「まだ」は yet。|2
He has ___ left the office.|just|yet|ever|since|現在完了で「たった今」は just。|2
She has never ___ abroad.|traveled|travel|travels|traveling|has never + 過去分詞。|1
We ___ known each other for ten years.|have|has|are|were|主語 we の現在完了は have known。|1
The system has been down ___ noon.|since|for|during|while|noon は起点なので since。|2
How long ___ you lived in Japan?|have|has|did|are|現在完了の疑問文は Have you + 過去分詞。|1
He has ___ his wallet, so he cannot pay.|lost|lose|losing|loses|過去の紛失が今に影響。has lost。|2
I have not met the new manager ___.|yet|already|just|ever since|「まだ会っていない」は not ... yet。|2
Our team has completed five tasks ___ far.|so|by|since|in|so far は「これまでのところ」。|3
This is the first time I have ___ this software.|used|use|using|uses|the first time + have + 過去分詞。|3
She ___ worked at this company since April.|has|have|is|was|主語 she の現在完了は has。|1
''',
'modal': '''
You ___ wear a helmet in this area. It is required.|must|might|can|would|義務・必要なら must。|1
You ___ share your password with anyone. It is prohibited.|must not|do not have to|may|might|must not は禁止。不要を示す don't have to と区別。|1
We ___ finish this today; the deadline is next week.|do not have to|must not|cannot|should not have|義務がない場合は do not have to。|2
___ I use this computer?|May|Must not|Should not|Needn't|許可を丁寧に求める May I ～?。|1
You ___ back up important files regularly.|should|wouldn't|mustn't|may not|推奨・助言は should。|1
He ___ speak English and Japanese fluently.|can|must not|had to|ought|能力なら can。|1
The lights are off. They ___ be at home, but I'm not sure.|might|must not|have to|shouldn't have to|不確かな可能性は might。|2
Employees ___ arrive before 9 a.m. according to the rule.|must|might|would|could have|規則上の義務は must。|1
You ___ bring a laptop; computers will be provided.|need not|must not|cannot|should not|持参不要は need not。禁止ではない。|2
We ___ leave early if the meeting finishes soon.|may|must not|had to|ought not|条件次第で可能なら may。|2
She ___ be tired after working all night.|must|can not to|shouldn't to|may to|強い推量には must be。|2
You ___ download files from unknown websites.|should not|need not to|must to|may to|避けるべき行動への助言は should not。|1
''',
'passive': '''
This software ___ by thousands of users.|is used|uses|is using|used|利用される側が主語。is + 過去分詞。|1
The email ___ yesterday.|was sent|sent|is sending|has send|昨日送られたので過去の受動態 was sent。|1
The files ___ every night.|are backed up|back up|is backing up|backed up|複数の files がバックアップされる。are backed up。|2
The new office ___ next year.|will be opened|will open by|will be opening by|has opened|「開設される」未来の受動態は will be + 過去分詞。|2
English ___ in many countries.|is spoken|speaks|is speaking|spoke|英語が話されるので is spoken。|1
The documents must ___ before Friday.|be submitted|submit|submitted|be submitting|助動詞の受動態は must be + 過去分詞。|2
The room ___ when we arrived.|was being cleaned|was cleaning|has cleaned|cleaned|到着時に清掃されている途中。was being cleaned。|3
The product ___ in Japan.|is made|makes|making|has make|製品は作られる側。is made。|1
The server has ___ repaired.|been|be|being|was|現在完了受動は has been + 過去分詞。|3
Our questions ___ by the instructor.|were answered|answered|were answering|answer|質問が回答されたため were answered。|2
The windows ___ once a week.|are cleaned|clean|is cleaned|cleaned|複数形 windows の現在受動態は are cleaned。|1
A new policy ___ last month.|was introduced|introduced|is introducing|will introduce|導入された過去の受動態 was introduced。|2
''',
'gerund': '''
I want ___ a programmer.|to become|becoming|become|became|want to + 動詞の原形。|1
She enjoys ___ books in English.|reading|to read|read|reads|enjoy の目的語には動名詞。|1
We look forward to ___ from you.|hearing|hear|heard|to hear|look forward to の to は前置詞。後ろは -ing。|2
Please let me ___ the document.|check|to check|checking|checked|let + 人 + 動詞の原形。|2
He decided ___ a new language.|to learn|learning|learn|learned|decide to + 動詞の原形。|1
Thank you for ___ us.|helping|help|to help|helped|前置詞 for の後は動名詞。|1
They avoided ___ the same error.|making|to make|make|made|avoid + 動名詞。|2
I hope ___ you soon.|to see|seeing|see|saw|hope to + 動詞の原形。|1
The manager made us ___ the plan.|revise|to revise|revising|revised|make + 人 + 動詞の原形。|2
Would you mind ___ the window?|opening|to open|open|opened|mind + 動名詞。|2
It is important ___ carefully.|to read|reading to|read to|reads|It is + 形容詞 + to不定詞。|1
I am interested in ___ software.|developing|develop|to develop|developed|前置詞 in の後には動名詞。|2
She promised ___ on time.|to arrive|arriving|arrive|arrived|promise to + 動詞の原形。|2
We finished ___ the report.|writing|to write|write|written|finish + 動名詞。|1
He is good at ___ problems.|solving|solve|to solve|solved|at は前置詞。後ろは動名詞。|1
We need ___ the system.|to update|updating to|update to|updated to|need to + 動詞の原形。|1
''',
'comparison': '''
This version is ___ than the old one.|faster|fast|fastest|more fast|than があるので比較級 faster。|1
This is the ___ solution of the three.|best|better|good|most better|3つの中の最上級は best。|1
The new monitor is as ___ as the old one.|large|larger|largest|more large|as ～ as の間には原級。|1
Our team is ___ than theirs.|smaller|small|smallest|most small|than の前は比較級 smaller。|1
This task is ___ difficult than I expected.|more|most|many|much more most|複数音節の形容詞 difficult は more difficult。|2
Her explanation was ___ than mine.|clearer|clear|clearest|more clearly|than の前は形容詞の比較級 clearer。|1
Today is the ___ day this week.|busiest|busier|busy|more busy|the ～ this week なら最上級 busiest。|2
The test was not as ___ as I thought.|hard|harder|hardest|more hard|not as + 原級 + as。|1
This process takes ___ time than before.|less|few|many|most|time は不可算名詞。「より少ない」は less。|2
My laptop is ___ powerful than yours.|more|most|many|much more most|powerful の比較級は more powerful。|1
The more you practice, the ___ you become.|better|best|good|well|the 比較級, the 比較級の構文。|3
Among these tools, this one is the ___ expensive.|least|less|little|fewer|the least expensive は最も安価。|3
''',
'relative': '''
The engineer ___ called you is on vacation.|who|which|where|when|人を説明する主格関係代名詞 who。|1
This is the program ___ I developed.|that|who|where|when|物を説明する目的格の that。|1
I visited the city ___ I was born.|where|which one|who|whose|「生まれた場所」なので関係副詞 where。|2
The person ___ desk is near mine is a manager.|whose|who|which|where|所有を示す whose + 名詞。|3
The laptop ___ was purchased yesterday is new.|which|who|where|when|物が主語の関係代名詞 which。|1
Do you know the woman ___ is speaking?|who|which|where|when|人を説明する who。|1
This is the office ___ we usually meet.|where|who|whose|what|場所 + where + 主語・動詞。|2
The report ___ she wrote was helpful.|that|who|where|whose|物に関する目的格関係代名詞 that。|2
I remember the day ___ we first met.|when|who|which one|whose|時を説明する関係副詞 when。|2
The man ___ car was stolen called the police.|whose|who|which|when|whose は「その人の」。|3
The website ___ provides the service is popular.|that|who|where|when|物を主語として説明する that。|1
Students ___ study every day often improve.|who|which|where|when|人を主語として説明する who。|1
''',
'preposition': '''
The meeting begins ___ 2 p.m.|at|on|in|by|時刻には at。|1
Our office is closed ___ Sundays.|on|at|in|for|曜日には on。|1
The project starts ___ April.|in|at|on|by|月には in。|1
Please submit the form ___ Friday.|by|until|during|since|by Friday は金曜までに（期限）。|1
We worked ___ 6 p.m. yesterday.|until|by|since|during|until は動作・状態の継続の終点。|2
This package was sent ___ email.|by|in|on|at|送信手段は by email。|2
The information is ___ the website.|on|in|at|by|ウェブサイト上は on the website。|1
She is responsible ___ customer support.|for|to|of|by|be responsible for ～「～を担当」。|2
He is interested ___ programming.|in|at|on|for|be interested in ～。|1
This product is different ___ that one.|from|to be|at|on|be different from ～。|2
Please reply ___ my message.|to|for|with|at|reply to + メッセージ。|1
The office is located ___ Nagoya.|in|on|at|by|都市・地域を表す位置は in。|1
We discussed the plan ___ the meeting.|during|by|since|until|会議の最中という期間は during。|2
He has lived here ___ five years.|for|since|during|by|five years は期間。for。|1
The deadline was extended ___ Monday.|to|at|in|from|extend ～ to + 新しい期限。|3
She arrived ___ the station at noon.|at|to|in|on|駅など具体的な場所への到着は arrive at。|1
They traveled ___ train.|by|on a|in the|at|交通手段を一般的に表す by train。|1
The manager is absent ___ work today.|from|on|at|by|be absent from work。|2
You can access the system ___ your smartphone.|from|at|since|until|アクセス元は from。|2
The file is attached ___ this email.|to|for|at|on|be attached to ～「～に添付」。|2
This feature is useful ___ beginners.|for|at|of|on|be useful for ～「～にとって役立つ」。|1
Please pay attention ___ the instructions.|to|in|of|by|pay attention to ～。|2
''',
'conjunction': '''
If it ___ tomorrow, we will stay inside.|rains|will rain|rained|rain|条件節 if の中では未来でも現在形。|1
I will call you when I ___ home.|get|get will|will get|got tomorrow|時を表す when 節は未来でも現在形。|2
___ he was tired, he finished the report.|Although|Because of|Despite of|During|although + 主語・動詞で逆接。|2
We canceled the event ___ it was raining.|because|although|unless|despite|理由を述べる because + 文。|1
Take an umbrella ___ it rains.|in case|despite|because of|during|in case は「～に備えて」。|3
You cannot enter ___ you have an ID card.|unless|because|although|when even|unless は「～しない限り」。|2
I was studying ___ my phone rang.|when|despite|unless|because of|突然の出来事を示す when 節。|1
She speaks slowly ___ everyone can understand.|so that|because of|despite|unless|目的を表す so that + 文。|2
___ completing the task, he went home.|After|Because|Although|Unless|after + 動名詞で「～した後」。|2
We will begin as soon as everyone ___.|arrives|will arrive|arrived tomorrow|arriving|as soon as の未来時の節は現在形。|2
He studied hard, ___ he passed the exam.|so|but|although|unless|原因・結果をつなぐ so。|1
I like tea, ___ my colleague prefers coffee.|while|because|unless|therefore|対比を表す while。|2
We went out ___ the heavy rain.|despite|although|because|even though|despite の後には名詞句。|3
___ you need help, please contact us.|If|Unless not|Despite|Because of|条件「必要なら」は if。|1
''',
'article': '''
She is ___ engineer.|an|a|the only|none|engineer は母音の音で始まる単数可算名詞。an。|1
I bought ___ new laptop yesterday.|a|an|many|much|new は子音の音で始まる。a new laptop。|1
He gave me ___ useful advice.|some|an|a|many|advice は不可算名詞。some advice。|2
We need more ___ about this issue.|information|informations|an information|many information|information は不可算名詞。複数 -s を付けない。|2
There are three ___ on the desk.|boxes|box|boxs|a box|three の後は複数形 boxes。|1
___ moon goes around the Earth.|The|A|An|Many|月を一意の天体として言う場合は the moon。|1
I had ___ breakfast at seven.|breakfast|a breakfast|an breakfast|the a breakfast|通常の食事名では冠詞を付けない。|2
She has ___ umbrella.|an|a|some an|many an|umbrella は母音で始まるので an。|1
We have only a little ___ left.|time|times|a time|many time|time は「時間」の意味で不可算名詞。|1
There isn't ___ water in the bottle.|much|many|a few|several|water は不可算名詞。much。|2
He has ___ books in his bag.|a few|a little|much|an|books は可算複数。a few。|2
They gave us two pieces of ___.|advice|advices|an advice|many advice|advice は不可算。two pieces of advice。|3
''',
'wordform': '''
Please read the instructions ___.|carefully|careful|care|more careful|動詞 read を修飾するのは副詞 carefully。|1
This is a very ___ solution.|effective|effectively|effect|effected|名詞 solution の前には形容詞 effective。|1
We need to improve customer ___.|satisfaction|satisfy|satisfied|satisfying|customer の後は名詞 satisfaction。|2
The system operates ___.|smoothly|smooth|smoothness|smoothing|動詞 operates を修飾する副詞 smoothly。|1
Her ___ was clear and concise.|explanation|explain|explained|explaining to|主語の核となる名詞 explanation。|2
We made a final ___ yesterday.|decision|decide|decisive|decidingly|a final の後には名詞 decision。|1
He is a ___ developer.|skilled|skill|skillfully|skills|名詞 developer を修飾する形容詞 skilled。|2
The company grew ___.|rapidly|rapid|rapidity|rapids|動詞 grew を修飾する副詞 rapidly。|1
Teamwork is ___ for this project.|essential|essence|essentially|essentials|be 動詞の補語として形容詞 essential。|2
We need a more ___ approach.|practical|practically|practice|practicedly|approach を修飾する形容詞 practical。|2
The new feature increased ___.|productivity|productive|productively|produce|increased の目的語は名詞 productivity。|3
He responded to the question ___.|politely|polite|politeness|politer|動詞 responded を修飾する副詞 politely。|1
The information is highly ___.|reliable|reliably|reliance|rely|be 動詞の後は形容詞 reliable。|2
They completed the work ___.|successfully|successful|success|succeed|動詞 completed を修飾する副詞 successfully。|1
The ___ of the document matters.|accuracy|accurate|accurately|accurating|the ～ of の位置は名詞 accuracy。|3
A ___ schedule helps everyone.|flexible|flexibility|flexibly|flex|名詞 schedule を修飾する形容詞 flexible。|2
''',
'conditional': '''
If I ___ more time, I would study abroad.|had|have|will have|having|現実と異なる仮定は if + 過去形、would + 原形。|3
If she ___ here, she could help us.|were|is|will be|being|仮定法では If she were ～ も使用する。|3
If it is sunny tomorrow, we ___ hiking.|will go|went|going|had gone|現実に起こり得る未来の条件は if + 現在形、will + 原形。|1
If I had known, I ___ you.|would have told|will tell|told|would tell yesterday|過去に反する仮定は would have + 過去分詞。|3
Unless you hurry, you ___ the train.|will miss|missed|had missed|missing|unless は if ～ not。未来の結果は will miss。|2
If I were you, I ___ that offer.|would accept|will accept yesterday|accepting|accepted tomorrow|If I were you, I would ～ は定番表現。|2
If he studied harder, he ___ better grades.|would get|will got|gets yesterday|had get|仮定法過去の結果は would + 動詞の原形。|3
If you heat ice, it ___.|melts|will melted|melted always|melting|普遍的な事実は if + 現在形、現在形。|1
If we had left earlier, we ___ the bus.|would have caught|will catch|catch|had catching|過去に反する仮定は would have caught。|3
I wish I ___ more English vocabulary.|knew|know|will know|knowing|I wish + 過去形は現在の事実に反する願望。|3
If the printer doesn't work, ___ the help desk.|contact|contacted|to contacting|will contacting|if + 現在形、命令形。|1
If he calls, I ___ you immediately.|will inform|informed|have informed yesterday|informing|現実の未来の条件には will + 原形。|1
''',
}
for cat, rows in G.items():
    for line in rows.strip().splitlines():
        parts=[x.strip() for x in line.split('|')]
        if len(parts)!=7: raise ValueError((cat,line,len(parts)))
        stem, answer,*rest=parts
        a,b,c,exp,level=rest
        add(cat,stem,answer,[a,b,c],exp,int(level))

# Extra grammar variants using controlled patterns to increase breadth without inflating repeated stems.
extra=[
('agreement','The software ___ correctly on this device.','runs',['run','running','ran'],'software は単数扱い。普段の動作は runs。',1),
('agreement','Neither of the options ___ available.','is',['are','be','have'],'neither of ～ は原則単数扱い。',2),
('tense','I ___ the backup before leaving last night.','checked',['check','checking','will check'],'last night は過去。checked。',1),
('tense','They ___ a video conference at the moment.','are having',['have yesterday','had tomorrow','has'],'at the moment は現在進行形。',1),
('perfect','I have ___ my homework already.','done',['did','do','doing'],'have + 過去分詞 done。',1),
('perfect','We have not seen him ___ Monday.','since',['for','during','until'],'Monday は起点なので since。',1),
('modal','Visitors ___ sign in at reception. It is mandatory.','must',['might','would','could have'],'mandatory = 義務。must sign in。',1),
('modal','You ___ worry; the issue is already resolved.','do not need to',['must not','cannot to','should to'],'「心配する必要がない」は do not need to。',2),
('passive','The results ___ tomorrow.','will be announced',['announce','will announce by','announcing'],'結果が発表されるので未来の受動態。',2),
('passive','The password ___ regularly for security.','is changed',['changes','changing','is changing by'],'変更される側なので is changed。',2),
('gerund','They agreed ___ the contract.','to sign',['signing','sign','signed'],'agree to + 原形。',2),
('gerund','She stopped ___ during the presentation.','talking',['to talk','talk','talked'],'stop doing は「～するのをやめる」。',2),
('comparison','This manual is ___ to read than that one.','easier',['easy','easiest','most easy'],'than の前は比較級 easier。',1),
('comparison','This is one of the ___ teams in the company.','largest',['larger','large','more large'],'one of the + 最上級 + 複数名詞。',3),
('relative','The book ___ I borrowed is useful.','that',['who','where','when'],'物を修飾する目的格関係代名詞。',1),
('relative','This is the reason ___ she left early.','why',['who','which','whose'],'reason を説明する関係副詞 why。',3),
('preposition','The conference takes place ___ November.','in',['on','at','by'],'月は in November。',1),
('preposition','The report is due ___ noon.','by',['since','during','until'],'期限は by noon。',2),
('conjunction','I stayed home ___ I felt sick.','because',['although','unless','despite'],'理由を示す because + 文。',1),
('conjunction','We can start ___ the manager arrives.','when',['despite','because of','unless not'],'到着時に、という意味の when。',1),
('article','Can you give me ___ water?','some',['a','an','many'],'water は不可算名詞。some water。',1),
('article','We need ___ hour to finish.','an',['a','many','few'],'hour は h を発音せず母音で始まるため an。',2),
('wordform','The results were ___.','surprising',['surprisingly','surprise','surprisedly'],'結果が驚くべきものなので形容詞 surprising。',2),
('wordform','She gave a ___ presentation.','detailed',['detail','details','detailedly'],'名詞 presentation を修飾する形容詞。',2),
('conditional','If you study regularly, your English ___.','will improve',['improved yesterday','would improving','has improve'],'現実的な未来の結果には will + 原形。',1),
('conditional','If I had a car, I ___ to work.','would drive',['will drove','drive yesterday','driving'],'現在の仮定は would + 原形。',3),
]
for c,s,a,w,e,l in extra: add(c,s,a,w,e,l)

# Vocabulary: sentence + correct + 3 unambiguous contextual distractors + Japanese brief rationale + level
V={
'vocab_general': '''
The weather forecast ___ rain tomorrow.|predicts|borrows|repairs|refuses|predict は「予測する」。|1
Please ___ this form before submitting it.|complete|destroy|forget|avoid|complete は「記入を完了する」。|1
I could not ___ his handwriting.|understand|purchase|divide|borrow|understand は「理解する」。|1
The museum is ___ on Mondays.|closed|hungry|expensive|alive|closed は「閉まっている」。|1
Please ___ the instructions carefully.|follow|lend|divide|ignore|follow instructions は「指示に従う」。|1
The road is ___ because of construction.|blocked|delicious|silent|generous|blocked は「通行を妨げられた」。|2
She has a strong ___ to succeed.|desire|weather|object|receipt|desire は「願望」。|2
This medicine should ___ the pain.|relieve|invite|collect|publish|relieve は「和らげる」。|2
It is ___ to bring an ID card to the exam.|necessary|ancient|narrow|wooden|necessary は「必要な」。|1
I ___ your help with the project.|appreciate|hesitate|divide|refuse|appreciate は「感謝する」。|2
The city has a large ___ of about two million.|population|temperature|permission|furniture|population は「人口」。|2
The bridge was built ___ 50 years ago.|approximately|angrily|rarely|carelessly|approximately は「およそ」。|2
He is ___ for arranging the event.|responsible|terrible|similar|possible|responsible for は「責任を持つ」。|1
The book provides useful ___ for beginners.|information|permission|furniture|weather|information は「情報」。文脈上学習者に有用。|1
The government will ___ a new rule next year.|introduce|destroy|lend|forget|introduce は「導入する」。|2
It is important to ___ enough sleep.|get|lend|print|repair|get enough sleep は「十分に眠る」。|1
This room is ___ for up to 30 people.|suitable|tired|hungry|furious|suitable for は「～に適する」。|2
The restaurant is located in a ___ area.|quiet|sleeping|broken|digital|quiet area は「静かな地域」。|1
We need to ___ the cause of the problem.|identify|decorate|deliver|celebrate|identify は「特定する」。|2
Her answer was ___ and easy to understand.|clear|bitter|heavy|empty|clear は「明確な」。|1
There is a ___ between the two designs.|difference|deadline|mistake|permission|difference は「違い」。|1
Please ___ your seat belt before takeoff.|fasten|publish|borrow|forget|fasten は「締める」。|2
The price has ___ significantly this year.|increased|washed|folded|borrowed|increase は「増加する」。|1
The company wants to ___ costs.|reduce|borrow|paint|discover|reduce costs は「コスト削減」。|1
We must ___ the environment.|protect|interrupt|borrow|remove|protect は「守る」。|1
This is a ___ opportunity to learn.|valuable|crowded|wooden|sleepy|valuable は「価値がある」。|2
He explained the ___ of the new policy.|purpose|temperature|furniture|engine|purpose は「目的」。|2
The result was ___ from what we expected.|different|hungry|round|sleeping|different from は「～と異なる」。|1
There are several ___ to this approach.|advantages|temperatures|schedules|windows|advantages は「利点」。|2
The store will ___ at 8 p.m.|close|grow|arrive|borrow|店舗が営業を終えるのは close。|1
The instructions are very ___.|simple|hungry|wooden|curly|simple は「簡単な」。|1
She was ___ to hear the good news.|delighted|absent|broken|local|delighted は「喜んだ」。|2
Please ___ the word in a dictionary.|look up|look after|look for|look into|look up a word は「単語を調べる」。|2
We had to ___ the meeting because of the storm.|postpone|invent|repair|improve|postpone は「延期する」。|2
His explanation was not ___.|accurate|empty|round|hungry|accurate は「正確な」。|2
We ___ on public transportation every day.|rely|paint|celebrate|divide|rely on は「～に頼る」。|2
You should ___ your skills regularly.|improve|waste|break|refuse|improve は「向上させる」。|1
The team reached an ___ after a long discussion.|agreement|apartment|entrance|accident|reach an agreement は「合意する」。|2
We need to find a ___ to this issue.|solution|furniture|population|schedule|solution to は「解決策」。|1
The manager will ___ the final decision.|announce|borrow|ignore|wash|announce は「発表する」。|1
She is very ___ and always arrives on time.|punctual|hungry|wooden|famous|punctual は「時間に正確な」。|2
The train was ___ by heavy snow.|delayed|painted|invited|borrowed|delayed は「遅れた」。|1
We must ___ the rules of this facility.|obey|borrow|repair|reduce|obey は「従う」。|1
The information was ___ from several sources.|collected|borrowed|painted|heated|collect information は「情報を収集する」。|2
The results will be ___ next week.|published|cooked|borrowed|repaired|publish results は「結果を公表する」。|2
Please remain ___ during the announcement.|silent|modern|delicious|expensive|remain silent は「静かにする」。|2
They made an ___ to fix the issue.|effort|engine|island|entrance|make an effort は「努力する」。|2
The building is ___ to the station.|adjacent|ancient|ordinary|healthy|adjacent to は「隣接して」。|3
We need to ___ between fact and opinion.|distinguish|deliver|decorate|repair|distinguish between は「区別する」。|3
His comments were ___ to the topic.|relevant|wooden|hungry|broken|relevant to は「関連がある」。|3
The project was ___ despite several delays.|successful|hungry|wooden|circular|successful は「成功した」。|1
''',
'vocab_business': '''
Please find the document ___ to this email.|attached|hidden|borrowed|deleted|attached to this email は「添付されている」。|1
We need to meet the project ___.|deadline|temperature|population|vehicle|deadline は「締切」。|1
The client requested a price ___.|estimate|hobby|journey|festival|estimate は「見積もり」。|2
Please ___ receipt of this message.|confirm|divide|erase|borrow|confirm receipt は「受信を確認する」。|2
Our team will ___ the application next week.|launch|borrow|fold|drink|launch an application は「公開・提供開始する」。|1
The server is currently ___.|unavailable|delicious|ancient|curious|unavailable は「利用できない」。|1
Could you ___ the meeting to Thursday?|reschedule|destroy|decorate|lend|reschedule は「日程を変更する」。|2
Please ___ the file to the shared folder.|upload|borrow|paint|doubt|upload は「アップロードする」。|1
The engineers fixed a software ___.|bug|recipe|ticket|garden|bug は「ソフトウェアの不具合」。|1
We need to ___ the database regularly.|back up|turn off|look after|break down|back up は「バックアップする」。|1
The service will be ___ for maintenance tonight.|offline|delicious|nearby|wooden|offline は「利用停止・オフライン」。|1
Please ___ the error message in your report.|include|borrow|celebrate|avoid|include は「含める」。|1
The network ___ improved after the upgrade.|performance|temperature|population|furniture|performance は「性能」。|2
The update includes several security ___.|improvements|recipes|journeys|celebrations|improvements は「改善点」。|2
The customer submitted a support ___.|request|bridge|library|mountain|request は「依頼」。|1
Our manager will ___ the proposal tomorrow.|review|borrow|paint|ignore|review は「確認・検討する」。|1
We need your ___ before proceeding.|approval|temperature|furniture|weather|approval は「承認」。|2
The team identified a potential security ___.|risk|garden|ticket|recipe|risk は「リスク・危険性」。|1
This tool can ___ repetitive tasks.|automate|decorate|ignore|lend|automate は「自動化する」。|2
The company plans to ___ its operations overseas.|expand|reduce to zero|forget|borrow|expand は「拡大する」。|2
Please ___ the software to the latest version.|update|invent|discuss|lend|update to the latest version は「最新版に更新する」。|1
The meeting ___ is attached to the email.|agenda|temperature|population|puzzle|agenda は「議題・進行予定」。|2
We should ___ the root cause of the failure.|investigate|celebrate|borrow|decorate|investigate は「調査する」。|2
The feature is still under ___.|development|temperature|weather|transportation|under development は「開発中」。|2
The system requires user ___.|authentication|decoration|transportation|celebration|authentication は「認証」。|3
The release was ___ because of a critical bug.|postponed|celebrated|borrowed|painted|postpone は「延期する」。|2
We have to ___ confidential information.|protect|advertise|publish|discard|機密情報は protect（保護する）。|1
The new process is more ___.|efficient|hungry|wooden|ancient|efficient は「効率的な」。|1
Please check the ___ of the data before importing it.|accuracy|temperature|decoration|festival|accuracy は「正確性」。|2
The team works closely with external ___.|partners|gardens|tickets|holidays|partners は「協力企業・相手先」。|1
We received positive customer ___.|feedback|weather|furniture|traffic|feedback は「反応・意見」。|1
Please ___ the changes in the system log.|record|borrow|paint|decorate|record は「記録する」。|2
The system is ___ with older devices.|compatible|hungry|sleepy|expensive|compatible with は「互換性がある」。|3
Our department handles technical ___.|inquiries|vegetables|journeys|paintings|inquiries は「問い合わせ」。|2
The ___ of the project is next Monday.|kickoff|temperature|population|furniture|kickoff は「開始会議・立ち上げ」。|2
We need to ___ enough staff for the event.|allocate|decorate|invent|borrow|allocate は「割り当てる」。|3
A clear ___ helps avoid misunderstandings.|specification|temperature|landscape|festival|specification は「仕様書・仕様」。|3
The new interface is more user-___.|friendly|hungry|wooden|empty|user-friendly は「使いやすい」。|2
The system ___ occurred at midnight.|failure|furniture|holiday|journey|system failure は「システム障害」。|2
Please ___ the contract before signing it.|review|borrow|paint|delete blindly|review は「見直す・精査する」。|1
The project is within ___.|budget|temperature|weather|furniture|within budget は「予算内」。|2
We will ___ the progress at the weekly meeting.|report|borrow|decorate|reduce silently|report progress は「進捗を報告する」。|1
The database stores sensitive customer ___.|records|gardens|recipes|festivals|records は「記録・データ」。|2
This change will improve system ___.|stability|weather|cooking|distance|stability は「安定性」。|3
Please create a ___ copy of the document.|backup|hungry|hollow|tired|backup copy は「予備の複製」。|2
The task is our top ___.|priority|temperature|holiday|garden|top priority は「最優先事項」。|1
The service is available to registered ___.|users|drivers only|tourists only|plants|users は「利用者」。|1
Please contact the ___ if you have questions.|administrator|mountain|vegetable|holiday|administrator は「管理者」。|1
The software license is ___ for one year.|valid|hungry|wooden|noisy|valid は「有効な」。|2
The engineer will ___ the faulty component.|replace|borrow|decorate|celebrate|replace は「交換する」。|1
'''
}
for cat,rows in V.items():
    for line in rows.strip().splitlines():
        parts=[x.strip() for x in line.split('|')]
        if len(parts)!=7: raise ValueError((cat,line,len(parts)))
        stem,answer,a,b,c,exp,level=parts
        add(cat,stem,answer,[a,b,c],exp,int(level))

# Reading passages. Each with 3 questions (answer + 3 alternatives + reason).
R=[
('''Starting next Monday, employees will use a new online form to request office supplies. The old paper form will no longer be accepted. Requests submitted by 3 p.m. will normally be processed on the same day.''',[
('What will employees use next Monday?','An online form',['A paper form','A phone call','A meeting room'],'新しい申請方法は online form。'),
('When are requests normally processed the same day?','When submitted by 3 p.m.',['When submitted after 6 p.m.','Only on Fridays','Only before 8 a.m.'],'by 3 p.m. が条件。'),
('What happens to the old paper form?','It will no longer be accepted',['It will be required','It will become digital by itself','It will be mailed'],'no longer be accepted は受付停止。')]),
('''Our company will hold a safety training session on Friday, October 16. All new employees must attend. The session will begin at 10 a.m. in Conference Room B and last approximately 90 minutes.''',[
('Who must attend the session?','All new employees',['Only managers','All customers','Only visitors'],'all new employees must attend とある。'),
('Where will the session take place?','Conference Room B',['The cafeteria','Conference Room A','The reception area'],'開催場所は Conference Room B。'),
('How long will the session last?','About 90 minutes',['About 30 minutes','About 2 hours','All day'],'approximately 90 minutes。')]),
('''A customer reported that the application was running slowly yesterday afternoon. The support team checked the server and found unusually high traffic. After adding more capacity, the response time returned to normal.''',[
('What problem did the customer report?','The application was slow',['The password was missing','The screen was broken','The invoice was incorrect'],'running slowly とある。'),
('What did the team discover?','Unusually high traffic',['A power cut','A missing employee','A damaged keyboard'],'high traffic が原因として見つかった。'),
('What improved the response time?','Adding more capacity',['Changing the password','Canceling the service','Reducing office hours'],'容量を増強した後に通常の応答時間に戻った。')]),
('''The library near the station has changed its opening hours. From April, it opens at 9 a.m. instead of 10 a.m. on weekdays. Weekend hours remain unchanged, and the library still closes at 6 p.m. every day.''',[
('What changed in April?','Weekday opening time',['Weekend closing time','Membership fees','The library location'],'平日の開館時間が変わった。'),
('When does the library open on weekdays now?','9 a.m.',['10 a.m.','8 a.m.','6 p.m.'],'opens at 9 a.m. instead of 10 a.m.。'),
('What time does the library close?','6 p.m. every day',['5 p.m. on weekdays','7 p.m. on weekends','10 a.m. every day'],'still closes at 6 p.m. every day。')]),
('''Please note that maintenance of the internal network is scheduled for Saturday from 1 a.m. to 4 a.m. During this period, employees may not be able to access shared files. Email services will remain available.''',[
('When is the maintenance scheduled?','Saturday, 1 a.m. to 4 a.m.',['Friday, 1 p.m. to 4 p.m.','Saturday, 9 a.m. to noon','Sunday, 1 a.m. to 4 a.m.'],'Saturday from 1 a.m. to 4 a.m.。'),
('Which service might be unavailable?','Shared files',['Email','Telephone lines','The building elevator'],'shared files にアクセスできない可能性。'),
('Which service will remain available?','Email',['Shared files','The internal network','Printing services'],'Email services will remain available。')]),
('''Mika joined the sales department in June. During her first month, she attended product training and accompanied experienced colleagues on customer visits. From July, she began handling small accounts by herself.''',[
('Which department did Mika join?','Sales',['Accounting','Human resources','Engineering'],'sales department とある。'),
('What did she do in her first month?','Attend training and customer visits',['Manage large accounts alone','Design the company logo','Prepare payroll'],'研修と顧客訪問への同行を行った。'),
('When did she start handling accounts alone?','July',['May','June','September'],'From July とある。')]),
('''Due to a delay in shipping, the new monitors will arrive on Wednesday rather than Monday. Employees who need a monitor urgently should contact the IT help desk. The help desk may provide a temporary device.''',[
('Why will the monitors arrive later?','A shipping delay',['A price increase','An office move','A software update'],'Due to a delay in shipping。'),
('When are they expected to arrive?','Wednesday',['Monday','Tuesday','Friday'],'Wednesday rather than Monday。'),
('What should employees do if they need one urgently?','Contact the IT help desk',['Buy one themselves immediately','Cancel all meetings','Call the shipping company directly'],'IT help desk に連絡する。')]),
('''The team tested two versions of a website. Version A loaded in 2.1 seconds on average, while Version B loaded in 1.4 seconds. Both versions had similar error rates, so the team selected Version B for the next release.''',[
('Which version loaded faster?','Version B',['Version A','Both were equally fast','Neither was tested'],'1.4 秒の B が 2.1 秒の A より速い。'),
('Why did the team select Version B?','It loaded faster with similar error rates',['It had twice as many errors','It was more expensive','It used a different language'],'速度優位かつエラー率が同程度。'),
('What was the average loading time of Version A?','2.1 seconds',['1.4 seconds','3.5 seconds','0.7 seconds'],'Version A loaded in 2.1 seconds。')]),
('''Visitors to the Osaka office must register at reception on the first floor. They will receive a temporary ID card that should be returned before leaving. Visitors are not permitted to enter the server room without an employee escort.''',[
('Where should visitors register?','At reception on the first floor',['At the server room','At the parking area','At the cafeteria'],'reception on the first floor とある。'),
('What should visitors return before leaving?','A temporary ID card',['A laptop','A parking ticket','A uniform'],'temporary ID card should be returned。'),
('What is needed to enter the server room?','An employee escort',['An online order','A new password only','A visitor survey'],'without an employee escort は入室不可。')]),
('''Employees can now work remotely up to two days per week with their manager’s approval. They must record their remote-work days on the company calendar by Thursday of the previous week. The policy starts on December 1.''',[
('How many days of remote work are allowed per week?','Up to two days',['One full week','Exactly three days','Unlimited days'],'up to two days per week。'),
('What approval is required?','Manager approval',['Customer approval','Government approval','No approval'],'with their manager’s approval。'),
('When must remote-work days be recorded?','By the previous Thursday',['On Friday after the remote work','At the end of the month','By the previous Monday'],'by Thursday of the previous week。')]),
('''A software company surveyed 200 users about a new mobile application. Of the respondents, 140 said the navigation was easy, while 35 reported difficulties finding settings. The company plans to redesign the settings menu based on the feedback.''',[
('How many users were surveyed?','200',['140','35','175'],'surveyed 200 users。'),
('What difficulty did 35 users report?','Finding settings',['Logging in','Making a payment','Opening emails'],'difficulties finding settings。'),
('What does the company plan to redesign?','The settings menu',['The company logo','The payment system','The entire office'],'redesign the settings menu。')]),
('''The recruitment seminar begins at 1:30 p.m. and lasts one hour. Participants should arrive 10 minutes early for registration. After the presentation, there will be a short question-and-answer session.''',[
('When does the seminar begin?','1:30 p.m.',['1 p.m.','1:20 p.m.','2:30 p.m.'],'begins at 1:30 p.m.。'),
('When should participants arrive?','1:20 p.m.',['1:30 p.m.','1:40 p.m.','2:20 p.m.'],'開始10分前は 1:20 p.m.。'),
('What follows the presentation?','A question-and-answer session',['A written exam immediately','A lunch break','A building tour'],'After the presentation に Q&A。')]),
('''A factory reduced its electricity use by installing energy-efficient lighting and replacing older machines. During the first three months, its electricity consumption fell by 12 percent compared with the same period last year.''',[
('What did the factory replace?','Older machines',['All employees','The building location','Its suppliers'],'replacing older machines。'),
('What was installed?','Energy-efficient lighting',['A new parking lot','Extra elevators','A larger kitchen'],'energy-efficient lighting。'),
('How much did electricity consumption fall?','12 percent',['3 percent','20 percent','50 percent'],'fell by 12 percent。')]),
('''The customer support desk usually closes at 6 p.m. However, during the year-end holiday period, it will close at 4 p.m. from December 28 to December 30. Normal hours resume on January 4.''',[
('When does support usually close?','6 p.m.',['4 p.m.','Noon','8 p.m.'],'usually closes at 6 p.m.。'),
('When will it close at 4 p.m.?','December 28–30',['January 4–6','Every Friday','All of November'],'December 28 to December 30。'),
('When will normal hours resume?','January 4',['December 30','January 1','February 4'],'resume on January 4。')]),
('''Before launching the new website, the design team asked six employees to complete five common tasks. Four participants finished all tasks without assistance. The other two had trouble with the search function, which was revised before launch.''',[
('How many employees took part?','Six',['Four','Two','Five'],'six employees とある。'),
('How many finished all tasks without help?','Four',['Two','Five','Six'],'four participants。'),
('What was revised before launch?','The search function',['The office layout','The password policy','The company name'],'search function was revised。')]),
]
for passage,items in R:
    for stem,answer,wrongs,exp in items:
        add('reading',stem,answer,wrongs,exp,2 if len(passage)>320 else 1,passage)

# Record source type and validate.
seen_stems=set()
for q in questions:
    key=(q['stem'],q.get('passage',''))
    if key in seen_stems: print('duplicate',q['id'],key)
    seen_stems.add(key)
assert len(questions)>=300,len(questions)
assert len(set(q['id'] for q in questions))==len(questions)
for q in questions:
    assert 0<=q['answer']<4
    assert q['explanation']
counts=collections.Counter(q['cat'] for q in questions)
print('total',len(questions),'bycat',counts)
(root/'questions.json').write_text(json.dumps({'categories':[{'id':id,'name':name,'group':group,'guide':guide} for id,name,group,guide in cats],'questions':questions},ensure_ascii=False,indent=2),encoding='utf8')
