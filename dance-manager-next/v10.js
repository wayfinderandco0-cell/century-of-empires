/* Dance Manager Next V10: use the approved marketing headline and preserved real navigation. */
(function(){
  'use strict';
  if(typeof marketing!=='function')return;
  const previouslyRenderedMarketing=marketing;
  marketing=function(){
    return previouslyRenderedMarketing()
      .replace('Your entire studio.<br><em>One beautiful</em><br>place to grow.','More than<br>a <em>dance</em> website.')
      .replace('Bring dancers, classes, competitions, schedules, billing and families together. Built around the people who make dance happen.','The complete dance studio management platform for studios, dancers, competitions and families.')
      .replace('THE COMPLETE DANCE PLATFORM · CONCEPT','STUDIOS · DANCERS · COMPETITIONS · ALL TOGETHER')
      .replace('Explore the studio platform','See the platform');
  };
  const stylesheet=document.createElement('link');
  stylesheet.rel='stylesheet';stylesheet.href='./v10.css?v=10-photo-1';
  document.head.appendChild(stylesheet);
  render();
})();