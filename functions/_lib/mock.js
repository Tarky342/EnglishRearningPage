export function mockTutor(q,action){
  const explanation=action==='simplify'?`「${q.choices[q.answer]}」が正解です。基本ルールを短く考えてみましょう。${q.explanation}`:`正解は「${q.choices[q.answer]}」です。${q.explanation}`;
  return{title:action==='practice'?'確認問題に挑戦':'文法のポイント',explanation,keyPoint:q.explanation,hint:'主語と時を表す語に注目しましょう。',check:{stem:q.cat==='agreement'?'The offices ___ at nine every weekday.':`Which option is a correct example of the rule? (${q.id})`,choices:q.cat==='agreement'?['open','opens']:['Option A','Option B'],answerIndex:0,reasoning:q.cat==='agreement'?'The offices は複数なので open を使います。':'これは表示テスト用のダミー問題です。'}};
}
