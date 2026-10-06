---
tail: 0.6
---
<!-- Written by `showtime new --from-storyboard` from storyboard.md: the Narration column, one line per shot, in
     order. Each {at=...} pins a line where its shot starts in the voice timeline (the shot's start
     minus 0.3 s of picture per narrated shot before it), so the shots keep the storyboard's lengths
     where the voice fits. Edit the words freely; keep the headings (they name the scenes).
     showtime voice script narration.md -o voice
     showtime retime . --from-voice voice/timeline.json --total 123 -->

## shot-1
In 1999, Francis Crick wrote that light would be the ideal signal for switching neurons, then called the idea rather far-fetched. This week, it won a Nobel Prize.

## shot-2
Karl Deisseroth, Peter Hegemann and Georg Nagel share the prize for discoveries about light-gated ion channels. Four steps, three guesses.

## shot-3 {pause_after=3.2}
Step one: an alga fifteen thousandths of a millimetre wide that swims toward light. Guess: how much faster than your eye does it react?

## shot-4
The Nobel Committee says: over twenty times faster. About half a millisecond after light hits its eyespot, an electrical impulse appears.

## shot-5
Step two: the switch. Peter Hegemann proposed that one protein could catch light and form a channel. People doubted it. Georg Nagel put algal genes into frog eggs, and when light hit, the channels opened.

## shot-6
Around one in the morning on 4 August 2004, Edward Boyden saw the first neuron carrying the alga's channel fire in blue light. By 2007, the Committee says, it worked in living mice.

## shot-7 {pause_after=3.2}
Step three: our toy model, an educational demo. A thin fibre sends blue, yellow or red light into brain tissue. Guess: which colour reaches deepest?

## shot-8
Red: about one and a half millimetres deep, against one for blue. But our model ignores absorption outside blood, so read every depth as rough. Reaching deeper takes more light, and more light means heat.

## shot-9
Tissue turns absorbed light into heat: a 2019 study measured 0.2 to 2 degrees Celsius of warming. In our toy model, pulsing the light cuts it: from about three and a half degrees to about six tenths of a degree.

## shot-10 {pause_after=3.2}
How many neurons can one degree of warming recruit? Guess: hundreds, thousands, or tens of thousands?

## shot-11
In our toy model: blue, about sixteen thousand; yellow, about thirty-one thousand.

## shot-12
Step four: the limit. Visible light cannot penetrate deep into brain tissue. Far-fetched, Crick wrote in 1999. Not any more.

## shot-13
Educational demos of this year's Nobel Prizes, made with showtime.
