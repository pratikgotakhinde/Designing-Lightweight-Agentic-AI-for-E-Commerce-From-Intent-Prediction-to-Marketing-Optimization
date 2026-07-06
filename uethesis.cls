%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% uethesis.cls
%% Author : Iftikhar Ahmed
%% Created: 09/02/2025
%% Version: 1.0
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{uethesis}[09/02/2025 v1.1 University of Europe for Applied Sciences Latex Class]

% --------------------------------------------------
% Load the base class
% --------------------------------------------------
\LoadClass[a4paper,12pt]{report}

% --------------------------------------------------
% Required packages
% --------------------------------------------------
\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{graphicx}
\RequirePackage{titlesec}
\RequirePackage[nottoc]{tocbibind} % Don't list the ToC itself in the ToC
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\RequirePackage{natbib}          % Harvard style citations
\RequirePackage{setspace}
\RequirePackage{caption}
\RequirePackage{tocloft}
\RequirePackage{etoolbox}
\RequirePackage{xcolor}
\RequirePackage{ifthen}

% --------------------------------------------------
% Page geometry and margins
% --------------------------------------------------
\geometry{
  left=3cm,
  right=3cm,
  top=2.5cm,
  bottom=2.5cm
}

% --------------------------------------------------
% Header and footer
% --------------------------------------------------
\pagestyle{fancy}
\fancyhf{}               % Clear header/footer
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\thepage}  % Center page number in the footer

% --------------------------------------------------
% Line spacing
% --------------------------------------------------
\setstretch{1.25}

% --------------------------------------------------
% Rename "Contents" to "Table of Contents"
% --------------------------------------------------
\renewcommand{\contentsname}{Table of Contents}

% --------------------------------------------------
% Table of Contents and numbering
% --------------------------------------------------
% Front matter -> roman page numbers
\newcommand{\frontmatter}{%
  \pagenumbering{roman}%
}

% Main matter -> arabic page numbers
\newcommand{\mainmatter}{%
  \clearpage
  \pagenumbering{arabic}%
}

% --------------------------------------------------
% Chapter heading: number and title on the same line
% --------------------------------------------------
\titleformat{\chapter}[hang]
  {\bfseries\Huge}
  {\chaptername\ \thechapter\quad}
  {0pt}{\Huge}

% --------------------------------------------------
% Figures and Tables numbering
% --------------------------------------------------
\renewcommand{\thetable}{\thechapter.\arabic{table}}
\renewcommand{\thefigure}{\thechapter.\arabic{figure}}

% Captions: tables above, figures below
\captionsetup[table]{position=above}
\captionsetup[figure]{position=below}

% --------------------------------------------------
% Harvard citation style
% --------------------------------------------------
\bibliographystyle{agsm}  % Harvard style

% --------------------------------------------------
% Hard-coded University Info
% --------------------------------------------------
\newcommand{\universityname}{University of Europe for Applied Sciences, Potsdam}
\newcommand{\universitylogo}{ue-logo.pdf}

% --------------------------------------------------
% User-settable info
% --------------------------------------------------
\newcommand{\thesistitle}{}
\newcommand{\thesisauthor}{}
\newcommand{\matriculation}{}
\newcommand{\firstsupervisor}{}
\newcommand{\secondsupervisor}{}
\newcommand{\submissiondate}{}
\newcommand{\department}{}
\newcommand{\major}{}
\newcommand{\degree}{}
\newcommand{\theabstract}{} % User will redefine this in the main file

% --------------------------------------------------
% Abstract printing macro
% --------------------------------------------------
\newcommand{\printabstract}{%
  \ifx\theabstract\empty
    % Do nothing if abstract is empty
  \else
    \chapter*{Abstract}%
    \addcontentsline{toc}{chapter}{Abstract}%
    \theabstract%
  \fi
}

% --------------------------------------------------
% Title page macro (Updated order & text size)
% --------------------------------------------------
\newcommand{\makethesistitle}{%
  \begin{titlepage}
    \centering
    
    % Thesis title at the top
    {\Huge \bfseries \thesistitle}\par\vspace{2cm}
    
    % Slightly larger university logo
    \includegraphics[width=0.75\textwidth]{\universitylogo}\\[2cm]
    
    % Author
    \ifx\thesisauthor\empty
      % do nothing
    \else
      {\large \textbf{Author:} \thesisauthor}\\[0.5cm]
    \fi

    % Matriculation
    \ifx\matriculation\empty
      % do nothing
    \else
      {\large \textbf{Matriculation:} \matriculation}\\[0.5cm]
    \fi
    
    % Degree with major
    \ifx\degree\empty
      {\large \textbf{Degree:} Thesis}\\[0.5cm]
    \else
      {\large \textbf{Degree:} \degree}\\[0.5cm]
    \fi
    
    % First supervisor
    \ifx\firstsupervisor\empty
      % do nothing
    \else
      {\large \textbf{First Supervisor:} \firstsupervisor}\\[0.5cm]
    \fi
    
    % Second supervisor
    \ifx\secondsupervisor\empty
      % do nothing
    \else
      {\large \textbf{Second Supervisor:} \secondsupervisor}\\[0.5cm]
    \fi
    
    % Bottom aligned: Larger Department & University Name
    \vfill
    \ifx\submissiondate\empty
      % do nothing
    \else
      {\large \textbf{Submission Date:} \submissiondate}\\
    \fi
    {\Large \textbf{\department}\par} % Increased text size
    {\Large \textbf{\universityname}}  % Increased text size
    
  \end{titlepage}
}

% --------------------------------------------------
% Default Author Declaration
% --------------------------------------------------
\newcommand{\authordeclaration}{%
\chapter*{Author Declaration}
I hereby declare that this thesis is my own work and that I have clearly
acknowledged all sources used in its creation. No portion of the work
referred to in this thesis has been submitted in support of an application
for another degree or qualification at this or any other university or
institute of learning.

\vspace{2cm}
\noindent
Signature: \rule{5cm}{0.5pt} \hfill Date: \rule{5cm}{0.5pt}
}

% --------------------------------------------------
% Begin thesis command
% --------------------------------------------------
% 1) Title page
% 2) Front matter (roman numbering)
% 3) Author Declaration
% 4) Abstract (printed by \printabstract, which also adds it to the ToC)
% 5) Table of Contents, then Lists of Tables & Figures (on separate pages)
% 6) Switch to main matter (arabic numbering)
\newcommand{\beginthesis}{%
  \makethesistitle
  \frontmatter
  \authordeclaration
  \clearpage
  \printabstract
  \clearpage
  \tableofcontents
  \clearpage
  \listoftables
  \clearpage
  \listoffigures
  \mainmatter
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% End of Class File
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
