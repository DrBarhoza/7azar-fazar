(function(global){
  "use strict";
  const E=global.RummikubEngine;
  function tileHTML(tile){
    const c=tile.joker?"joker":tile.color, text=tile.joker?"★ J":tile.number;
    return `<div class="rum-tile ${c}" draggable="true" data-tile-id="${tile.id}" title="${tile.joker?"Joker":`${tile.color} ${tile.number}`}">${text}</div>`;
  }
  class RummikubBoard{
    constructor(root,puzzle,options={}){
      this.root=root; this.original=E.clone(puzzle); this.puzzle=E.clone(puzzle); this.options=options; this.history=[]; this.dragId=null; this.left=puzzle.timeLimit||60; this.timer=null; this.solutionTimer=null; this.step=-1; this.locked=false; this.render();
    }
    state(){return {table:E.clone(this.puzzle.table),rack:E.clone(this.puzzle.rack)};}
    render(){
      const leaveCount=(this.original.leaveOnRack||[]).length;
      this.root.innerHTML=`<div class="rum-shell"><div class="rum-head"><strong>${this.puzzle.title||"Rummikub Puzzle"}</strong><span class="rum-badge ${this.puzzle.gameTier||this.puzzle.difficulty}">${(this.puzzle.gameTier||this.puzzle.difficulty).toUpperCase()}</span><span class="rum-clock">01:00</span></div><div class="rum-table" data-zone="table">${this.puzzle.table.map((m,i)=>`<div class="rum-meld" data-zone="meld" data-meld="${i}">${m.map(tileHTML).join("")}</div>`).join("")}<div class="rum-meld" data-zone="new">+ New meld</div></div><div class="rum-rack-wrap"><div class="rum-rack-label">Team rack — ${leaveCount?`leave ${leaveCount} named tile${leaveCount===1?"":"s"}`:"play every tile"}</div><div class="rum-rack" data-zone="rack">${this.puzzle.rack.map(tileHTML).join("")}</div></div><div class="rum-actions"><button data-act="undo">↶ Undo</button><button data-act="reset">Reset</button><button class="rum-submit" data-act="submit">Submit</button><button class="rum-solution" data-act="solution">Show Solution</button><button data-act="prev">◀ Previous Step</button><button data-act="next">Next Step ▶</button></div><div class="rum-message"></div><div class="rum-step" hidden></div></div>`;
      this.clock=this.root.querySelector(".rum-clock"); this.message=this.root.querySelector(".rum-message"); this.stepBox=this.root.querySelector(".rum-step");
      this.root.querySelectorAll("[draggable=true]").forEach(el=>el.addEventListener("dragstart",e=>{if(this.locked)e.preventDefault();else this.dragId=el.dataset.tileId;}));
      this.root.querySelectorAll("[data-tile-id]").forEach(el=>el.addEventListener("click",()=>{if(this.options.onTileClick)this.options.onTileClick(el.dataset.tileId,this.locate(el.dataset.tileId));}));
      this.root.querySelectorAll("[data-zone]").forEach(zone=>{
        zone.addEventListener("dragover",e=>{if(!this.locked){e.preventDefault();zone.classList.add("dragover");}});
        zone.addEventListener("dragleave",()=>zone.classList.remove("dragover"));
        zone.addEventListener("drop",e=>{e.preventDefault();e.stopPropagation();zone.classList.remove("dragover");this.drop(this.dragId,zone,e);});
      });
      this.root.querySelectorAll("[data-act]").forEach(b=>b.addEventListener("click",()=>this.action(b.dataset.act)));
      this.updateClock();
    }
    locate(id){
      const ri=this.puzzle.rack.findIndex(t=>t.id===id); if(ri>=0)return {zone:"rack",index:ri};
      for(let mi=0;mi<this.puzzle.table.length;mi++){const ti=this.puzzle.table[mi].findIndex(t=>t.id===id);if(ti>=0)return {zone:"meld",meld:mi,index:ti};} return null;
    }
    saveHistory(){this.history.push(this.state());if(this.history.length>100)this.history.shift();}
    drop(id,zone,event){
      if(this.locked||!id)return; const from=this.locate(id);if(!from)return;this.saveHistory();
      const targetTile=event.target.closest("[data-tile-id]"),targetTileId=targetTile?.dataset.tileId;
      const before=targetTile&&event.clientX<targetTile.getBoundingClientRect().left+targetTile.getBoundingClientRect().width/2;
      const tile=from.zone==="rack"?this.puzzle.rack.splice(from.index,1)[0]:this.puzzle.table[from.meld].splice(from.index,1)[0];
      this.puzzle.table=this.puzzle.table.filter(m=>m.length);
      const target=zone.dataset.zone;
      if(target==="rack"){const at=this.puzzle.rack.findIndex(t=>t.id===targetTileId);this.puzzle.rack.splice(at<0?this.puzzle.rack.length:at+(before?0:1),0,tile);}
      else if(target==="new"||target==="table")this.puzzle.table.push([tile]);
      else{let mi=this.puzzle.table.findIndex(m=>m.some(t=>t.id===targetTileId));if(mi<0)mi=Math.min(Number(zone.dataset.meld),this.puzzle.table.length-1);const at=this.puzzle.table[mi].findIndex(t=>t.id===targetTileId);this.puzzle.table[mi].splice(at<0?this.puzzle.table[mi].length:at+(before?0:1),0,tile);}
      this.render();
    }
    action(action){
      if(action==="undo"&&this.history.length){const s=this.history.pop();this.puzzle.table=s.table;this.puzzle.rack=s.rack;this.render();}
      if(action==="reset")this.reset(false);
      if(action==="submit")this.submit();
      if(action==="solution")this.showSolution();
      if(action==="next")this.showStep(1);
      if(action==="prev")this.showStep(-1);
    }
    reset(restartTimer=false){this.stopSolution();this.puzzle=E.clone(this.original);this.history=[];this.locked=false;this.step=-1;this.render();if(restartTimer){this.left=this.original.timeLimit||60;this.start();}}
    submit(){
      const table=E.validateTable(this.puzzle.table), expected=new Set(this.original.leaveOnRack||[]), empty=this.puzzle.rack.length===expected.size&&this.puzzle.rack.every(t=>expected.has(t.id));
      if(table.ok&&empty){this.stop();this.message.textContent="SOLVED!";this.message.className="rum-message good";this.locked=true;if(this.options.onSolved)this.options.onSolved(this.left);}
      else{this.message.textContent=empty?("Not quite — some combinations are still invalid."):"Not quite — every rack tile must be played.";this.message.className="rum-message bad";if(this.options.onInvalid)this.options.onInvalid(table);}
    }
    start(){this.stop();this.left=this.original.timeLimit||60;this.updateClock();this.timer=setInterval(()=>{this.left--;this.updateClock();if(this.left<=0){this.stop();this.locked=true;this.message.textContent="TIME'S UP — review the solution when ready.";this.message.className="rum-message bad";if(this.options.onTimeout)this.options.onTimeout();}},1000);}
    stop(){if(this.timer){clearInterval(this.timer);this.timer=null;}}
    updateClock(){if(!this.clock)return;const seconds=Math.max(0,this.left),minutes=Math.floor(seconds/60),remainder=seconds%60;this.clock.textContent=`${String(minutes).padStart(2,"0")}:${String(remainder).padStart(2,"0")}`;this.clock.classList.toggle("warn",this.left<=10);}
    showSolution(){this.stop();this.stopSolution();this.locked=true;this.step=-1;const steps=E.solutionSteps(this.original,this.original.solution?.finalTable||[]);if(!steps.length)return;const advance=()=>{this.showStep(1,steps);if(this.step<steps.length-1)this.solutionTimer=setTimeout(advance,700);};advance();}
    showStep(delta,providedSteps){
      const solution=this.original.solution||{};const steps=providedSteps||E.solutionSteps(this.original,solution.finalTable||[]);if(!steps.length){this.message.textContent="No reviewed solution is stored.";return;}
      this.step=Math.max(0,Math.min(steps.length-1,this.step+delta));const step=steps[this.step];
      if(step.final&&solution.finalTable){this.animateToFinal(solution.finalTable);return;}
      this.stepBox.hidden=false;this.stepBox.textContent=`Step ${this.step+1} of ${steps.length}: ${step.text}`;
      if(step.tileId){const el=this.root.querySelector(`[data-tile-id="${step.tileId}"]`);if(el)el.classList.add("moving");const target=this.root.querySelector(`[data-meld="${step.toMeld}"]`);if(target)target.classList.add("solution-target");}
    }
    animateToFinal(finalTable){const old=new Map([...this.root.querySelectorAll("[data-tile-id]")].map(el=>[el.dataset.tileId,el.getBoundingClientRect()]));this.puzzle.table=E.clone(finalTable);const leave=new Set(this.original.leaveOnRack||[]);this.puzzle.rack=E.clone(this.original.rack.filter(t=>leave.has(t.id)));this.render();this.locked=true;this.root.querySelectorAll("[data-tile-id]").forEach(el=>{const was=old.get(el.dataset.tileId),now=el.getBoundingClientRect();if(was)el.animate([{transform:`translate(${was.left-now.left}px,${was.top-now.top}px)`,zIndex:20},{transform:"translate(0,0)",zIndex:1}],{duration:900,easing:"cubic-bezier(.2,.8,.2,1)"});});this.message.textContent="SOLUTION";this.message.className="rum-message good";}
    stopSolution(){if(this.solutionTimer){clearTimeout(this.solutionTimer);this.solutionTimer=null;}}
    destroy(){this.stop();this.stopSolution();this.root.innerHTML="";}
  }
  global.RummikubBoard=RummikubBoard;
})(typeof window!=="undefined"?window:globalThis);
