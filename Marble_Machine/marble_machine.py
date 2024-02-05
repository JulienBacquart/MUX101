import mido
# import py5
from pygame import mixer
from collections import namedtuple
from collections import deque

from crank import Crank
from toggle import Toggle
from marble import Marble

### Midi Processing
# Open the midi file
mid = mido.MidiFile('./data/Marble Machine.mid')

# Midi parameters
ticks_per_beat = mid.ticks_per_beat
tempo = mid.tracks[0][1].tempo
# print(f'{ticks_per_beat=}, {tempo=}, BPM={int(mido.tempo2bpm(tempo, (4,4)))}')

# Convenient 'Class' to map from midi values to 'real' notes
Instrument = namedtuple("Instrument", "ind name")

# In the case of the midi note 36 and 38, they could be bass or drum note,
# so we need to have separate dictionnaries
DRUM_NOTES_DICT = {
    36 : Instrument(0, 'drum_kick'),
    38 : Instrument(1, 'drum_snare'),
    57 : Instrument(2, 'drum_crash'),   
}
drum_min_ind, drum_max_ind = 0, 2 

VIBRAPHONE_NOTES_DICT = {
    71 : Instrument(3, 'vibraphone_B4'),
    72 : Instrument(4, 'vibraphone_C5'),
    74 : Instrument(5, 'vibraphone_D5'),
    76 : Instrument(6, 'vibraphone_E5'),
    78 : Instrument(7, 'vibraphone_FSH5'),
    79 : Instrument(8, 'vibraphone_G5'),
    81 : Instrument(9, 'vibraphone_A5'),
    83 : Instrument(10, 'vibraphone_B5'),
    84 : Instrument(11, 'vibraphone_C6'),
    86 : Instrument(12, 'vibraphone_D6'),
    88 : Instrument(13, 'vibraphone_E6'),
}
vibraphone_min_ind, vibraphone_max_ind = 3, 13

BASS_NOTES_DICT = {
    28 : Instrument(14, 'bass_E1'),
    31 : Instrument(15, 'bass_G1'),
    33 : Instrument(16, 'bass_A1'),
    35 : Instrument(17, 'bass_B1'),
    36 : Instrument(18, 'bass_C2'),
    38 : Instrument(19, 'bass_D2'),
    40 : Instrument(20, 'bass_E2'),
    42 : Instrument(21, 'bass_FSH2'),
    43 : Instrument(22, 'bass_G2'),
    45 : Instrument(23, 'bass_A2'),
    47 : Instrument(24, 'bass_B2'),
    48 : Instrument(25, 'bass_C3'),
    50 : Instrument(26, 'bass_D3'),
    52 : Instrument(27, 'bass_E3'),
    55 : Instrument(28, 'bass_G3'),
    57 : Instrument(29, 'bass_A3'),
    59 : Instrument(30, 'bass_B3'),
    60 : Instrument(31, 'bass_C4'),
    62 : Instrument(32, 'bass_D4'),
    64 : Instrument(33, 'bass_E4'), 
}
bass_min_ind, bass_max_ind = 14, 33

total_num_notes = len(DRUM_NOTES_DICT) + len(VIBRAPHONE_NOTES_DICT) + len(BASS_NOTES_DICT)

# Create the empty 'partition' = a list of lists of Boolean to know when we should be playing
# a specific instrument (=True) or not (= False)
BARS = 46 # we are only interested in the first 46 bars
# We have 4 quarter notes per bar (4 beats), but we want an 8th of a note resolution (240 ticks)
partition = [[False] * total_num_notes for _ in range(BARS * 8)]
# Duration of an eighth of note = duration of one cell in the partition, in millisecond
index_duration = int(mido.tick2second((ticks_per_beat / 2), ticks_per_beat, tempo) * 1000)
# print(f'index_duration: {index_duration} ms')

# Process the midi file to create the 'partition' for use in the program
for track in mid.tracks[1:4]: 
    if track.name == 'Drums':
        notes_dict = DRUM_NOTES_DICT
        print(f'Processing : Drums...')
    elif track.name == 'Vibraphone':
        print(f'Processing : Vibraphone...')
        notes_dict = VIBRAPHONE_NOTES_DICT
    else:
        print(f'Processing : Bass...')
        notes_dict = BASS_NOTES_DICT
    
    global_time = 0
    for msg in track:
        if not msg.is_meta:
            global_time += msg.time
            index = int(global_time / 240)
            if index >= len(partition):
                break
            # For a specific 'note' we find the indice of the instrument associated with it
            elif msg.type == 'note_on':
                partition[index][notes_dict[msg.note].ind] = True


### Initialization of the graphics, sounds etc.
# Graphic dimensions
WIDTH, HEIGHT = 1000, 600
TOP_OFFSET = 20
BOTTOM_OFFSET = TOP_OFFSET
LEFT_OFFSET = 275

# Colors
BG_COLOR = "#18242e"
STROKE_COLOR = 225
FILL_COLOR = 155

# Calculate the value of the gravity to fall the height of the screen in a specific time t (= T frames)
TARGET_FPS = 60 # frames/sec
FALL_TIME = 1 # sec  
T = FALL_TIME * TARGET_FPS # sec * frames/sec = frames
# a = 2 * y / t², where y is the height
Marble.gravity = 2 * (HEIGHT - TOP_OFFSET - BOTTOM_OFFSET) / (T * T)

# Initializing the marbles
BALL_DIAMETER = 35
Marble.ball_diameter = BALL_DIAMETER
Marble.top_offset = TOP_OFFSET
Marble.bottom_offset = BOTTOM_OFFSET
Marble.stroke_color = STROKE_COLOR
Marble.fill_color = FILL_COLOR
# Calculate x position for each marble
x_positions_list = [i * ((WIDTH - LEFT_OFFSET) / (len(VIBRAPHONE_NOTES_DICT) * 2)) 
                      for i in range(1,len(VIBRAPHONE_NOTES_DICT) * 2)
                     if i % 2 == 1]

# For each note, we can have several marbles (one bouncing, one falling, one ready to fall...)
# So for each row we have a Deque of marbles
# When a marble fall out of the screen, we pop it from the deque, and append a new one ready to fall
marble_list = [deque([Marble(x)]) for x in x_positions_list]

# Loading the list of samples file
samples_list = [f'./data/samples_drum/{instrument.name}.wav' for instrument in DRUM_NOTES_DICT.values()]
samples_list += [f'./data/samples_vibraphone/{instrument.name}.wav' for instrument in VIBRAPHONE_NOTES_DICT.values()]
samples_list += [f'./data/samples_bass/{instrument.name}.wav' for instrument in BASS_NOTES_DICT.values()]

# Mixer initialization
NUM_CHANNELS = 32
mixer.init()
mixer.set_num_channels(NUM_CHANNELS)

# Loading the samples
sounds_list = [mixer.Sound(sample) for sample in samples_list]
silence = mixer.Sound('./data/silence_sample.wav') # Hello darkness my old friend
for sound in sounds_list:
    sound.set_volume(0.5) 

# Initialize the crank handle
CRANK_SIZE = 175
CRANK_X = WIDTH - CRANK_SIZE/1.5
CRANK_Y = HEIGHT - CRANK_SIZE/1.6
Crank.stroke_color = STROKE_COLOR
Crank.fill_color = FILL_COLOR
crank = Crank(CRANK_X, CRANK_Y, CRANK_SIZE)
    
# Time keeping
previous_time = 0
custom_time = 0
previous_index = 0
previous_sound_index = 0

# "BASS" points data
BASS_X = WIDTH - 60
BASS_Y = 85 + 30
BASS_SCALE = 0.45
BASS_LINES = (
    (10, 15),(76, 32),(76, 32),(25, 86),(25, 86),(81, 72),(81, 72),(37, 141),(10, 15),(37, 141), # B
    (106, 29),(85, 113),(106, 29),(166, 156),(92, 86),(132, 85), # A
    (171, 10),(142, 46),(142, 46),(196, 65),(196, 65),(166, 103), # S
    (238, 27),(200, 47),(200, 47),(239, 76),(239, 76),(207, 126), # S
)

# "DRUMS" points data
DRUMS_X = WIDTH - 110
DRUMS_Y = 165 + 30
DRUMS_SCALE = 0.8
DRUMS_LINES = (
    (6, 6),(53, 22),(53, 22),(25, 79),(6, 6),(25, 79), # D
    (65, 8),(83, 30),(83, 30),(59, 36),(59, 36),(83, 61),(65, 8),(55, 52), # R
    (96, 17),(88, 48),(88, 48),(122, 48),(122, 48),(112, 22), # U
    (139, 22),(126, 60),(139, 22),(148, 48),(148, 48),(170, 10),(170, 10),(179, 76), # M
    (200, 12),(182, 26),(182, 26),(204, 45),(204, 45),(185, 60), # S
)

# "TURN ME ->" points data
TURN_ME_X = WIDTH - 15
TURN_ME_Y = HEIGHT - 200
TURN_ME_SCALE = 0.5
TURN_ME_LINES = (
    (13, 59),(102, 15),(54, 38),(92, 115), # T
    (103, 44),(98, 81),(98, 81),(147, 77),(147, 77),(138, 40), # U
    (171, 11),(154, 114),(171, 11),(229, 50),(229, 50),(165, 68),(165, 68),(222, 108), # R
    (234, 82),(250, 28),(250, 28),(285, 78),(285, 78),(281, 24), # N
    (316, 104),(339, 15),(339, 15),(360, 45),(360, 45),(382, 16),(382, 16),(406, 122), # M
    (435, 34),(478, 35),(435, 34),(419, 86),(427, 58),(453, 61),(419, 86),(465, 91), # E
    (157, 195),(269, 134),(269, 134),(372, 176),(358, 129),(372, 176),(328, 206),(372, 176), # ->
)

# Toggle buttons to mute bass and drums
TOGGLE_DIAMETER = 18
TOGGLE_WIDTH = 72
Toggle.diameter = TOGGLE_DIAMETER
Toggle.stroke_color = STROKE_COLOR
Toggle.fill_color = FILL_COLOR

BASS_TOGGLE_X = WIDTH - 155
BASS_TOGGLE_Y = 115
bass_mute = Toggle(BASS_TOGGLE_X, BASS_TOGGLE_Y, TOGGLE_WIDTH, TOGGLE_DIAMETER)

DRUMS_TOGGLE_X = WIDTH - 155
DRUMS_TOGGLE_Y = 225
drums_mute = Toggle(DRUMS_TOGGLE_X, DRUMS_TOGGLE_Y, TOGGLE_WIDTH, TOGGLE_DIAMETER)

### Setup function
def setup():
    global s_lines, t_lines, u_lines
    
    size(WIDTH, HEIGHT)
    smooth()
    window_title("Marble Machine")
    
    shape_mode(CENTER)
    rect_mode(CENTER)

    # Initialize shape objetcts
    with push_style():    
        stroke(STROKE_COLOR)
        
        # "TURN ME ->" shape
        s_lines = create_shape()
        with s_lines.begin_shape(LINES):
            s_lines.stroke_weight(6)
            s_lines.vertices(TURN_ME_LINES)
            s_lines.scale(TURN_ME_SCALE)

        # "BASS" shape
        t_lines = create_shape()
        with t_lines.begin_shape(LINES):
            t_lines.stroke_weight(7)
            t_lines.vertices(BASS_LINES)
            t_lines.scale(BASS_SCALE)
            
        # "DRUMS" shape
        u_lines = create_shape()
        with u_lines.begin_shape(LINES):
            u_lines.stroke_weight(4)
            u_lines.vertices(DRUMS_LINES)
            u_lines.scale(DRUMS_SCALE)

### Draw loop
def draw():
    global previous_time, custom_time, previous_index
    
    # Draw background 
    background(BG_COLOR)   
    
    # Draw "BASS"
    shape(t_lines, BASS_X, BASS_Y)
    
    # Bass mute toogle
    bass_mute.display()
    
    # Draw "DRUMS"
    shape(u_lines, DRUMS_X, DRUMS_Y)
    
     # Drums mute toogle
    drums_mute.display()
    
    # Draw "TURN ME ->"
    shape(s_lines, TURN_ME_X, TURN_ME_Y)
    
    # Time keeping
    time_multiplier = remap(crank.angle_velocity, 0, 0.2, 0, 1)
    current_time = millis()
    delta_time = current_time - previous_time
    # custom_time = real_time * the speed we crank the handle at
    custom_time += delta_time * time_multiplier
    previous_time = current_time
    current_index = int(custom_time / index_duration) % len(partition)    

    # Marbles falling + sound playing
    if (current_index != previous_index):
        for instrument, note in enumerate(partition[current_index]):            
            if note:
                # Play Sound if not muted
                if not (
                    (bass_mute.value and (bass_min_ind <= instrument <= bass_max_ind))
                    or 
                    (drums_mute.value and (drum_min_ind <= instrument <= drum_max_ind))
                ):
                    # We want to play sounds when the marble bounce on the bars at the bottom of the screen
                    # so we start by playing a silent sound for the duration of the fall
                    # and queue the note to play after
                    ch = silence.play(maxtime = FALL_TIME * 1000)
                    ch.queue(sounds_list[instrument])
                    ch.get_queue().fadeout(5 * index_duration)

                # Drop Marble
                if vibraphone_min_ind <= instrument <= vibraphone_max_ind:
                    deq = marble_list[instrument - vibraphone_min_ind]
                    # Clean-up out-of-screen marbles
                    while (deq[0].out_of_screen):
                        deq.popleft()
                    # Return the first non-falling marble
                    m = next((marble for marble in deq if marble.falling == False), None)
                    m.falling = True
                    m.opacity = 255
                    # Create a new marble to takes it spot
                    deq.append(Marble(m.orig_x))
        
        previous_index = current_index
    
    # Crank update + display
    crank.update()
    crank.display()
    
    # Marbles update + display
    for deq in marble_list:
        for marble in deq:
            marble.update()
            marble.display()

# Event to detect if the crank handle is turned (=click + drag on the crank objetct)
def mouse_dragged():
    crank.turn(mouse_x, mouse_y, pmouse_x, pmouse_y)

# Event to detect if the toggles buttons are clicked
def mouse_clicked():
    bass_mute.clicked(mouse_x, mouse_y)
    drums_mute.clicked(mouse_x, mouse_y)
     
# py5.run_sketch()
