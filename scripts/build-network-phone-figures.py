"""Build the five ebook-only Chapter 4 vertical teaching diagrams."""
from pathlib import Path
from html import escape
import textwrap
out=Path(__file__).resolve().parents[1] / 'book/figures'
data={
'museum-publication-ebook':('Publish one complete set at a time','Loopback museum lab: each numbered card is a later local state.',[
('Private original and unfinished outputs',['No visitor route; a hidden link is not a gate.']),
('1 · Revision 8 is incomplete',['Current selection stays at revision 7.','8 has a thumbnail, but no large image.','Visitor receives both approved 7 variants.']),
('2 · Revision 8 is complete and approved',['Expected output digests match.','Current selection advances to revision 8.','Visitor receives both approved 8 variants.']),
('3 · Conditional local withdrawal',['Current selection becomes none.','Revision floor remains 8.','Old local media URL is denied.']),
('The boundary of this proof',['A fresh loopback request follows this pointer.','Downloads, CDN caches and S3 origin policy need separate live checks before a global claim.'])]),
'balancer-choices-ebook':('Choose the balancer by its job','Three separate requirements; each path needs its own cost and failure check.',[
('1 · Web paths · ALB',['Browser HTTP','↓ ALB reads path','↓ Orders / returns groups']),
('2 · Partner protocol · NLB',['Partner UDP','↓ NLB carries flow','↓ Protocol targets']),
('3 · Packet inspection · GWLB',['Route tables','↓ GWLB endpoint','↓ GWLB','↓ Appliance fleet','Check route steering, appliance health, and the return path.']),
('Limits',['Conceptual choices, not a deployment recipe or measured price comparison.'])]),
'writer-conflict-ebook':('One slot, two promises is a failure','A tidy final row cannot erase an accepted receipt.',[
('Unsafe · Two disconnected writers',['First store: Alice 09:00 confirmed.','Second store: Bob 09:00 confirmed.','One confirmed receipt disappears.','Choosing one final row cannot undo either promise.']),
('Local control · One writer, checked handoff',['1 First confirms Alice; second remains closed.',"2 Stop first; copy and check Alice’s receipt.",'3 Open second only after the check passes.',"Bob’s 09:00 attempt stops.",'A different free slot may still be accepted.']),
('Limits',['Local SQLite rule; no AWS replication or distributed fence tested.'])]),
'dns-http-ebook':('A DNS answer is not the web request','The browser uses the answer for a separate connection.',[
('1 · Name lookup',['Browser → resolver → Route 53 record answer','Resolver returns the CloudFront destination.','Route 53 did not carry the HTTP request.']),
('2 · Separate web request',['HTTP path: browser → CloudFront']),
('Public guide',['A valid reusable response may come from edge cache.']),
('Private booking or invoice',['No shared cached answer; forward to ALB.','ALB selects service; service checks caller access.']),
('Design and limits',['Design cache and origin policies; test cross-user denial.','Conceptual only: TLS, network controls and data stores omitted.'])]),
'filter-ownership-ebook':('One request, two decisions','Follow one request down the gates.',[
('Customer request',["Alice asks for Bob’s repair."]),
('↓ Web request filter',['Inspect request shape and ordered rules.']),
('↓ Count or Allow: continue',['Block: stop before application.']),
('↓ If continued: ownership check',["Alice does not own Bob’s record.",'Deny the record read.']),
('Separate decisions',['A filter decision is not record permission.'])])}
for name,(title,subtitle,cards) in data.items():
 elems=[];y=28
 def text(s,bold=False):
  global y
  for line in textwrap.wrap(s,width=29 if bold else 33,break_long_words=False):
   elems.append(f'<text x="24" y="{y}" font-size="{18 if bold else 17}" font-weight="{700 if bold else 400}">{escape(line)}</text>');y+=25
 text(title,True);y+=5;text(subtitle);y+=18
 for heading,body in cards:
  start=y-20;idx=len(elems);text(heading,True);y+=7
  for s in body:text(s);y+=7
  end=y+3;elems.insert(idx,f'<rect x="10" y="{start}" width="340" height="{end-start}" rx="12" fill="#edf4f6" stroke="#527888"/>');y=end+35
 (out/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 {y}" width="360" height="{y}"><rect width="360" height="{y}" fill="white"/><g font-family="Arial, sans-serif" fill="#193746">'+''.join(elems)+'</g></svg>')
