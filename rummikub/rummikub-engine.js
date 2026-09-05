(function(global){
  "use strict";
  const COLORS = ["red","blue","black","orange"];
  const STATUS = Object.freeze({DRAFT:"draft", APPROVED:"approved", REJECTED:"rejected"});
  const clone = value => JSON.parse(JSON.stringify(value));
  const tileKey = tile => tile.joker ? "joker" : `${tile.color}-${tile.number}`;

  function isTile(tile){
    return !!tile && (tile.joker === true || (COLORS.includes(tile.color) && Number.isInteger(tile.number) && tile.number >= 1 && tile.number <= 13));
  }
  function jokerCount(meld){ return meld.filter(t=>t.joker).length; }
  function isRun(meld){
    if(!Array.isArray(meld) || meld.length < 3 || meld.some(t=>!isTile(t))) return false;
    const normal = meld.filter(t=>!t.joker);
    if(!normal.length || new Set(normal.map(t=>t.color)).size !== 1) return false;
    const nums = normal.map(t=>t.number).sort((a,b)=>a-b);
    if(new Set(nums).size !== nums.length) return false;
    const span = nums[nums.length-1] - nums[0] + 1;
    if(span > meld.length) return false;
    const spare = meld.length - span;
    return nums[0] - spare >= 1 || nums[nums.length-1] + spare <= 13;
  }
  function isGroup(meld){
    if(!Array.isArray(meld) || meld.length < 3 || meld.length > 4 || meld.some(t=>!isTile(t))) return false;
    const normal = meld.filter(t=>!t.joker);
    return normal.length > 0 && new Set(normal.map(t=>t.number)).size === 1 && new Set(normal.map(t=>t.color)).size === normal.length;
  }
  function isMeld(meld){ return isRun(meld) || isGroup(meld); }
  function flatten(table){ return (table || []).flat(); }
  function validateInventory(table, rack=[]){
    const counts = new Map();
    for(const tile of [...flatten(table), ...rack]){
      if(!isTile(tile)) return {ok:false, reason:"A tile has an invalid number or color."};
      const key = tileKey(tile), n = (counts.get(key)||0)+1;
      counts.set(key,n);
      if((key === "joker" && n > 2) || (key !== "joker" && n > 2)) return {ok:false, reason:`Too many copies of ${key}.`};
    }
    return {ok:true};
  }
  function validateTable(table){
    if(!Array.isArray(table) || !table.length) return {ok:false, reason:"The table must contain at least one meld."};
    for(let i=0;i<table.length;i++) if(!isMeld(table[i])) return {ok:false, reason:`Meld ${i+1} is not a legal run or group.`, meld:i};
    return {ok:true};
  }
  function structuralValidate(p){
    if(!p || typeof p !== "object") return {ok:false, reason:"Puzzle data is missing."};
    if(!/^RUM-[HE]-\d{3,}$/.test(p.id||"")) return {ok:false, reason:"Puzzle ID is invalid."};
    if(!["hard","expert"].includes(p.difficulty)) return {ok:false, reason:"Difficulty must be Hard or Expert."};
    if(!Object.values(STATUS).includes(p.status)) return {ok:false, reason:"Puzzle status is invalid."};
    if(!Array.isArray(p.table) || !Array.isArray(p.rack) || !p.rack.length) return {ok:false, reason:"Table and non-empty rack are required."};
    return {ok:true};
  }
  function canonicalMeld(meld, colorBlind=false){
    const normals = meld.filter(t=>!t.joker);
    const run = isRun(meld);
    return (run?"R":"G") + ":" + meld.map(t=>t.joker?"J":`${colorBlind?"C":t.color}${t.number}`).sort().join(",");
  }
  function canonicalPuzzle(p){
    const colorMap = new Map(); let next=0;
    const normalizeTile = t=>{
      if(t.joker) return {joker:true};
      if(!colorMap.has(t.color)) colorMap.set(t.color, String.fromCharCode(65+next++));
      return {color:colorMap.get(t.color), number:t.number};
    };
    const table=(p.table||[]).map(m=>m.map(normalizeTile).sort((a,b)=>(a.number||0)-(b.number||0))).map(m=>JSON.stringify(m)).sort();
    const rack=(p.rack||[]).map(normalizeTile).map(tileKey).sort();
    return JSON.stringify({table,rack});
  }

  function combinations(items, min=3, max=4){
    const out=[];
    function walk(start, chosen){
      if(chosen.length>=min) out.push(chosen.slice());
      if(chosen.length===max) return;
      for(let i=start;i<items.length;i++){ chosen.push(items[i]); walk(i+1,chosen); chosen.pop(); }
    }
    walk(0,[]); return out;
  }
  function meldCandidates(tiles){
    const candidates=[]; const unique=new Set();
    const jokers=tiles.filter(x=>x.tile.joker);
    const add=combo=>{
      const ids=combo.map(x=>x.index).sort((a,b)=>a-b), key=ids.join(",");
      if(!unique.has(key) && isMeld(combo.map(x=>x.tile))){unique.add(key);candidates.push(ids);}
    };
    // Groups are at most four tiles, so enumerate only tiles sharing a number.
    for(let n=1;n<=13;n++){
      const pool=tiles.filter(x=>x.tile.joker || x.tile.number===n);
      for(const combo of combinations(pool,3,4)) add(combo);
    }
    // Runs: enumerate consecutive windows and choose at most one physical copy
    // for each number; Jokers fill missing positions. This avoids 2^N brute force.
    for(const color of COLORS){
      for(let start=1;start<=11;start++) for(let end=start+2;end<=13;end++){
        const slots=[]; let missing=0;
        for(let n=start;n<=end;n++){
          const copies=tiles.filter(x=>!x.tile.joker && x.tile.color===color && x.tile.number===n);
          if(copies.length) slots.push(copies); else {missing++; slots.push([]);}
        }
        if(missing>jokers.length) continue;
        function choose(si,chosen){
          if(si===slots.length){
            const base=chosen.filter(Boolean); for(const js of combinations(jokers,missing,missing)) add([...base,...js]);
            return;
          }
          if(!slots[si].length) choose(si+1,[...chosen,null]);
          else slots[si].forEach(tile=>choose(si+1,[...chosen,tile]));
        }
        choose(0,[]);
      }
    }
    return candidates;
  }
  function solve(puzzle, limit=2){
    if(Array.isArray(puzzle.solverCoreMelds)){
      const coreSet=new Set(puzzle.solverCoreMelds),core=[],locked=[];
      (puzzle.table||[]).forEach((meld,i)=>(coreSet.has(i)?core:locked).push(clone(meld)));
      const scoped=solve({...puzzle,solverCoreMelds:undefined,table:core},limit);
      if(!scoped.solvable)return scoped;
      return {...scoped,solutions:scoped.solutions.map(table=>[...table,...clone(locked)])};
    }
    const tiles=[...flatten(puzzle.table), ...puzzle.rack].map((tile,index)=>({tile:clone(tile),index}));
    if(tiles.length > 34) return {solvable:false, solutions:[], count:0, truncated:true, reason:"Puzzle exceeds the interactive solver safety limit."};
    const candidates=meldCandidates(tiles);
    const byTile=Array.from({length:tiles.length},()=>[]);
    candidates.forEach((c,ci)=>c.forEach(i=>byTile[i].push(ci)));
    const solutions=[]; const seen=new Set();
    function walk(remaining, chosen){
      if(!remaining.size){
        const table=chosen.map(ci=>candidates[ci].map(i=>clone(tiles[i].tile)));
        const key=table.map(m=>canonicalMeld(m)).sort().join("|");
        if(!seen.has(key)){ seen.add(key); solutions.push(table); }
        return;
      }
      if(solutions.length>=limit) return;
      let pivot=null, options=null;
      for(const i of remaining){
        const valid=byTile[i].filter(ci=>candidates[ci].every(x=>remaining.has(x)));
        if(!valid.length) return;
        if(!options || valid.length<options.length){pivot=i; options=valid; if(valid.length===1) break;}
      }
      for(const ci of options){
        const next=new Set(remaining); candidates[ci].forEach(i=>next.delete(i));
        walk(next,[...chosen,ci]); if(solutions.length>=limit) break;
      }
    }
    walk(new Set(tiles.map(x=>x.index)),[]);
    return {solvable:solutions.length>0, solutions, count:solutions.length, truncated:solutions.length>=limit};
  }
  function solutionSteps(puzzle, finalTable){
    const rackIds=new Set((puzzle.rack||[]).map(t=>t.id));
    const startMembership=new Map(),finalMembership=new Map();
    (puzzle.table||[]).forEach(meld=>{const key=meld.map(t=>t.id).sort().join("|");meld.forEach(t=>startMembership.set(t.id,key));});
    finalTable.forEach(meld=>{const key=meld.map(t=>t.id).sort().join("|");meld.forEach(t=>finalMembership.set(t.id,key));});
    const steps=[];
    finalTable.forEach((meld,mi)=>meld.forEach((tile,ti)=>{
      if(rackIds.has(tile.id)||startMembership.get(tile.id)!==finalMembership.get(tile.id))steps.push({tileId:tile.id,text:`Place ${describeTile(tile)} in solution meld ${mi+1}.`,toMeld:mi,toIndex:ti});
    }));
    steps.push({text:"Confirm that every rack tile is played and every meld is legal.", final:true});
    return steps;
  }
  function describeTile(t){ return t.joker ? "Joker" : `${t.color} ${t.number}`; }
  function difficulty(puzzle, solution){
    const rack=puzzle.rack.length, start=puzzle.table, end=solution||[];
    const startSig=new Set(start.map(m=>canonicalMeld(m))), endSig=new Set(end.map(m=>canonicalMeld(m)));
    const affected=[...startSig].filter(x=>!endSig.has(x)).length;
    const joker=[...flatten(start),...puzzle.rack].some(t=>t.joker);
    const transfers=Math.max(0,affected-1), splits=Math.max(0,end.length-start.length);
    const score=Math.min(100, 34 + rack*5 + affected*5 + transfers*3 + splits*4 + (joker?7:0));
    return {score, difficulty:score>=78?"expert":"hard", rackTiles:rack, tilesMoved:rack+affected, meldsAffected:affected, transfers, splits, joker, estimatedComplexity:score>=88?"Very high":score>=78?"High":"Challenging"};
  }
  function validateForApproval(puzzle, existing=[]){
    const checks=[];
    const add=(name,result)=>checks.push({name,ok:!!result.ok,reason:result.reason||""});
    add("Puzzle structure",structuralValidate(puzzle));
    add("Starting table is legal",validateTable(puzzle.table));
    add("Legal tile inventory",validateInventory(puzzle.table,puzzle.rack));
    const solved=solve(puzzle,3);
    add("At least one solution",{ok:solved.solvable,reason:solved.reason||"No legal solution was found."});
    const final=solved.solutions[0];
    add("All rack tiles can be played",{ok:!!final,reason:"The solver could not play every rack tile."});
    add("Final table contains only legal melds",final?validateTable(final):{ok:false,reason:"No final table exists."});
    add("Stored solution is reproducible",{ok:!puzzle.solution || (!!final && validateTable(puzzle.solution.finalTable||puzzle.solution).ok),reason:"Stored solution is invalid."});
    add("Hard or Expert classification",{ok:["hard","expert"].includes(puzzle.difficulty),reason:"Only Hard and Expert puzzles may be approved."});
    const required=puzzle.referencePattern?3:(puzzle.difficulty==="expert"?5:4);
    const directCount=(puzzle.rack||[]).filter(tile=>(puzzle.table||[]).some(meld=>isMeld([...meld,tile]))).length;
    add("Required table reconstruction",{ok:!!final&&directCount<=1&&difficulty(puzzle,final).meldsAffected>=required,reason:directCount>1?"More than one rack tile has an obvious direct placement.":`The solution must rebuild at least ${required} existing melds.`});
    const canon=canonicalPuzzle(puzzle);
    add("Not an effective duplicate",{ok:!existing.some(p=>p.id!==puzzle.id && canonicalPuzzle(p)===canon),reason:"A logically equivalent puzzle already exists."});
    return {ok:checks.every(c=>c.ok),checks,solver:solved,analysis:final?difficulty(puzzle,final):null};
  }
  global.RummikubEngine={COLORS,STATUS,clone,tileKey,isTile,isRun,isGroup,isMeld,validateTable,validateInventory,structuralValidate,canonicalPuzzle,solve,solutionSteps,difficulty,validateForApproval,describeTile};
})(typeof window!=="undefined"?window:globalThis);
