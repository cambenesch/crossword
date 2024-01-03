#include <Wt/WApplication.h>
#include <Wt/WBreak.h>
#include <Wt/WContainerWidget.h>
#include <Wt/WLineEdit.h>
#include <Wt/WPushButton.h>
#include <Wt/WText.h>
#include <Wt/WTable.h>
#include <Wt/WInPlaceEdit.h>
#include <Wt/WValidator.h>
#include <Wt/WRegExpValidator.h>
#include <Wt/WStackedWidget.h>
#include <Wt/WCheckBox.h>
#include <Wt/WLineEdit.h>
#include <Wt/WMessageBox.h>
#include <Wt/>
#include <chrono>
#include <thread>
#include <cctype>
#include <time.h>
using namespace std;

class HelloApplication : public Wt::WApplication
{
public:
    HelloApplication(const Wt::WEnvironment& env);

private:
    // widgets
    Wt::WLineEdit* nameEdit_;
    Wt::WText* greeting_;
    Wt::WText* saveStatus_;
    Wt::WStackedWidget* crossword_; // 2 tables
    Wt::WTable* textTable_;
    Wt::WTable* colorTable_;

    // pointers to the elements in the tables
    vector<vector<Wt::WCheckBox*>> checkPtrs_{ 
        15, vector<Wt::WCheckBox*>(15) };
    vector<vector<Wt::WInPlaceEdit*>> letterPtrs_{ 
        15, vector<Wt::WInPlaceEdit*>(15) };
    vector<vector<Wt::WText*>> numberPtrs_{
        15, vector<Wt::WText*>(15) };

    // '_' = black or blank white, 'L' = letter filled out
    vector<vector<char>> letters{ 15, vector<char>(15, '_') }; 
    vector<vector<char>> savedLetters{ 15, vector<char>(15, '_') };
    // -1 = black, 0 = non-numbered white, n = numbered white
    vector<vector<int>> numbers{ 15, vector<int>(15, 0) };
    vector<vector<int>> savedNumbers{ 15, vector<int>(15, 0) };

    // methods connected to signals
    void setSaveStatus();
    void userColorUpdate(int i, int j);
    void userLetterUpdate(int i, int j);
    void updateCellDisplayColor(int i, int j);
    void checkpointSave();
    void checkpointRevert();
    void updateNumbering(int i, int j);
    bool solve();
    bool solveUnsaved();
    bool uploadFile();
};

/**
* upload a file
*/
bool HelloApplication::uploadFile() {
    // open a popup: current puzzle/solution will be lost!
    // then if user proceeds:
    //   hide crossword widgets
    //   create/show upload widgets
    // create a container: WFileUpload, WButton, WText
    // increase max file size to like 20mb
    // if file too big, report and allow reupload
    // if upload succeeds, check file extension
    // if bad extension, report and allow reupload
    // if good:
    //   hide the upload page widgets
    //   show the crossword widgets
    return true;
}

/**
* solve the puzzle! Returns whether it's solvable
* if unsaved, then not then prompts user to save
*/
bool HelloApplication::solve() {
    if (saveStatus_->text() == "Unsaved changes") {
        bool proceed = solveUnsaved();
        if (proceed) {
            checkpointRevert();
        }
        else {
            return false;
        }
    }
    // try to solve, will probably have to display progress bar
    //   involves querying the API, will be annoying
    if (savedNumbers[0][0] == -1) { // pretend this means unsolvable
        Wt::WMessageBox::show(
            "Unable to solve :(", "RIP", Wt::StandardButton::Ok);
        return false;
    }
    else { // pretend this means it's solvable
        savedLetters[0][0] = 'A';
        saveStatus_->setText("Unsaved changes");
        checkpointRevert(); // to update the display
        Wt::WMessageBox::show(
            "Solved!", "eskeetit", Wt::StandardButton::Ok);
        return true;
    }
}

/**
* show a popup message "Solving will erase unsaved changes!"
* return: true iff user wants to proceed
*/
bool HelloApplication::solveUnsaved() {
    Wt::StandardButton response = Wt::WMessageBox::show(
        "Solving will erase unsaved changes!",
        "Proceed?",
        Wt::StandardButton::Yes | Wt::StandardButton::Cancel
        );
    return response == Wt::StandardButton::Yes;
}

/**
* for a given cell i, j, update the crossword display color
*/
void HelloApplication::updateCellDisplayColor(int i, int j) {
    string color = numbers[i][j] == -1 ? "blackCell" : "whiteCell";
    colorTable_->elementAt(i, j)->setObjectName(color);
    textTable_->elementAt(i, j)->setObjectName(color);
    letterPtrs_[i][j]->lineEdit()->setObjectName(color);
}

/**
* for a given cell i, j, process a user checkbox click
*/
void HelloApplication::userColorUpdate(int i, int j) {
    numbers[i][j] = checkPtrs_[i][j]->isChecked() ? -1 : 0;
    updateCellDisplayColor(i, j);
    updateNumbering(i, j);
    if (numbers[i][j] != savedNumbers[i][j]) {
        saveStatus_->setText("Unsaved changes");
    }
    else {
        setSaveStatus();
    }
}

/**
* for a given cell i, j, process a user letter edit
*/
void HelloApplication::userLetterUpdate(int i, int j) {
    // check whether there's a character
    string text = letterPtrs_[i][j]->lineEdit()->text().toUTF8();
    if (text.size() && isalpha(text.at(0))) {
        letters[i][j] = toupper(text.at(0));
    }
    else { // the cell is blank (or black)
        letters[i][j] = '_';
    }
    string result(1, letters[i][j]);
    letterPtrs_[i][j]->setText(result);
    if (letters[i][j] != savedLetters[i][j]) {
        saveStatus_->setText("Unsaved changes");
    }
    else {
        setSaveStatus();
    }
}

/**
* check whether displayed puzzle == saved puzzle
* set saveStatus_ text accordingly
*/
void HelloApplication::setSaveStatus() {
    if (letters == savedLetters && numbers == savedNumbers) {
        saveStatus_->setText("All changes saved");
    }
    else {
        saveStatus_->setText("Unsaved changes");
    }
}

/**
* save current display as a checkpoint
*/
void HelloApplication::checkpointSave() {
    crossword_->setCurrentWidget(textTable_);
    savedLetters = letters;
    savedNumbers = numbers;
    saveStatus_->setText("All changes saved");
}

/**
* discard current display, revert to last checkpoint
*/
void HelloApplication::checkpointRevert() {
    crossword_->setCurrentWidget(textTable_);
    if (saveStatus_->text() == "All changes saved") {
        return;
    }
    letters = savedLetters;
    numbers = savedNumbers;
    for (int i = 0; i < 15; ++i) {
        for (int j = 0; j < 15; ++j) {
            string letter(1, letters[i][j]);
            checkPtrs_[i][j]->setChecked(numbers[i][j] == -1);
            letterPtrs_[i][j]->setText(letter);
            updateCellDisplayColor(i, j);
        }
    }
    updateNumbering(0, 0);
    saveStatus_->setText("All changes saved");
}

/**
* black cells were changed starting at i, j.
* Recompute the numbering, reflect it in:
*   numbers, numberPtrs_
*/
void HelloApplication::updateNumbering(int i, int j) {
    // find the most recent number
    int startPos = 15 * i + j - 1;
    int r = i;
    int c = j;

    // search until you hit 0, or you find a numbered cell
    while (startPos >= 0 && numbers.at(r).at(c) <= 0) {
        startPos--;
        r = startPos / 15;
        c = startPos % 15;
    }

    // the most recent number you found
    int startNum = startPos == -1 ? 0 : numbers.at(r).at(c);

    // update numbered cells
    for (int pos = startPos + 1; pos < 225; ++pos) {
        r = pos / 15;
        c = pos % 15;
        if (numbers.at(r).at(c) >= 0) { // white cell
            if (r == 0 || numbers[r - 1][c] == -1 ||
                c == 0 || numbers[r][c - 1] == -1) {
                // add a number
                numbers.at(r).at(c) = ++startNum;
                numberPtrs_.at(r).at(c)->setText(to_string(startNum));
            }
            else { // keep it blank
                numbers.at(r).at(c) = 0;
                numberPtrs_.at(r).at(c)->setText("");
            }
        }
        else { // black cell
            numberPtrs_.at(r).at(c)->setText("");
        }
    }
}

HelloApplication::HelloApplication(const Wt::WEnvironment& env)
    : Wt::WApplication(env)
{
    // style elements
    root()->setContentAlignment(Wt::AlignmentFlag::Center);
    setTitle("Hello world");
    string boxRule = "height:30px;width:30px;max-width:30px;text-align:center;border:2px solid black; position:relative;";
    string blackRule = "background-color:black;selection-background-color:black;selection-color:black;color:black;";
    styleSheet().addRule("[data-object-name=\"whiteCell\"]", boxRule);
    styleSheet().addRule("[data-object-name=\"blackCell\"]", boxRule + blackRule);
    // display:flex; justify-content:flex-start; align-content:flex-start;
    styleSheet().addRule("[data-object-name=\"number\"]", "font-size:10px; font-weight: bold; position:absolute; top:-1px; left:2px;");
    styleSheet().addRule("button", "margin:2px;");
    styleSheet().addRule(".dialog-layout", "background-color:lightgrey; text-align:center; border:2px solid dimgray; padding:10px;");

    // temporary: initialize random puzzle
    int randResult = rand() % 225;
    for (int i = 0; i < 15; ++i) {
        for (int j = 0; j < 15; ++j) {
            if (rand() % 7 == 0) {
                numbers[i][j] = -1; // black
            }
            else if (rand() % 5) {
                letters[i][j] = 'A' + rand() % 26; // fill with letter
            }
        }
    }

    // default widgets
    root()->addNew<Wt::WText>("Your fucking name, please? ");
    nameEdit_ = root()->addNew<Wt::WLineEdit>();
    Wt::WPushButton* button = root()->
        addNew<Wt::WPushButton>("Greet me, daddy.");
    root()->addNew<Wt::WBreak>();

    // crossword widget
    crossword_ = root()->addNew<Wt::WStackedWidget>();
    crossword_->setContentAlignment(Wt::AlignmentFlag::Center);
    textTable_ = crossword_->addNew<Wt::WTable>();
    colorTable_ = crossword_->addNew<Wt::WTable>();

    for (int i = 0; i < 15; ++i) {
        for (int j = 0; j < 15; ++j) {
            string letter(1, letters[i][j]);
            int number = numbers[i][j];

            string numberStr = number > 0 ? to_string(number) : "";
            Wt::WText* thisNumber = textTable_->elementAt(i, j)->
                addNew<Wt::WText>(numberStr);
            thisNumber->setObjectName("number");
            numberPtrs_[i][j] = thisNumber;

            Wt::WInPlaceEdit* thisText = textTable_->elementAt(i,j)->
                addNew<Wt::WInPlaceEdit>(letter);
            thisText->lineEdit()->setMaxLength(1);
            thisText->textWidget()->setMargin(20, Wt::Side::Top);

            thisText->setButtonsEnabled(false);
            letterPtrs_[i][j] = thisText;
            auto user_letter_update = [this, i, j] {
                userLetterUpdate(i, j);
            };
            thisText->lineEdit()->textInput().connect(user_letter_update);

            Wt::WCheckBox* thisColor = colorTable_->elementAt(i,j)->
                addNew<Wt::WCheckBox>();
            thisColor->setChecked(number == -1);
            checkPtrs_[i][j] = thisColor;
            auto user_color_update = [this, i, j] {
                userColorUpdate(i, j);
            };
            thisColor->checked().connect(user_color_update);
            thisColor->unChecked().connect(user_color_update);

            textTable_->elementAt(i, j)->setContentAlignment(
                Wt::AlignmentFlag::Middle | Wt::AlignmentFlag::Center);
            colorTable_->elementAt(i, j)->setContentAlignment(
                Wt::AlignmentFlag::Middle | Wt::AlignmentFlag::Center);
            updateCellDisplayColor(i, j);
            textTable_->elementAt(i, j)->resize(30, 30);
            colorTable_->elementAt(i, j)->resize(30, 30);
        }
    }
    //root()->addNew<Wt::WBreak>();

    // status text, crossword editing buttons
    saveStatus_ = root()->addNew<Wt::WText>("All changes saved");
    root()->addNew<Wt::WBreak>();

    Wt::WPushButton* editCellButton = root()->
        addNew<Wt::WPushButton>("Edit Letters");
    auto edit_cell_button = [this] {
        crossword_->setCurrentWidget(textTable_);
    };
    editCellButton->clicked().connect(edit_cell_button);

    Wt::WPushButton* editColorButton = root()->
        addNew<Wt::WPushButton>("Select Black Cells");
    auto edit_color_button = [this] {
        crossword_->setCurrentWidget(colorTable_);
    };
    editColorButton->clicked().connect(edit_color_button);

    Wt::WPushButton* saveEditsButton = root()->
        addNew<Wt::WPushButton>("Save Checkpoint");
    auto save_edits_button = [this] { checkpointSave(); };
    saveEditsButton->clicked().connect(save_edits_button);

    Wt::WPushButton* revertButton = root()->
        addNew<Wt::WPushButton>("Revert to Checkpoint");
    auto revert_button = [this] {checkpointRevert(); };
    revertButton->clicked().connect(revert_button);
    root()->addNew<Wt::WBreak>();

    // solve button and image uploading 
    Wt::WPushButton* solveButton = root()->
        addNew<Wt::WPushButton>("Solve");
    auto solve_button = [this] {solve(); };
    solveButton->clicked().connect(solve_button);

    Wt::WPushButton* uploadButton = root()->
        addNew<Wt::WPushButton>("Use New Image");
    auto upload_button = [this] {uploadFile(); };
    solveButton->clicked().connect(upload_button);
    root()->addNew<Wt::WBreak>();

    // greeting shit
    greeting_ = root()->addNew<Wt::WText>();
    auto greet = [this] {
        greeting_->setText("Hello there, " + nameEdit_->text());
    };
    button->clicked().connect(greet);

    // initialize numbering and saved puzzle
    updateNumbering(0, 0);
    checkpointSave();
}

int main(int argc, char** argv)
{
    return Wt::WRun(argc, argv, [](const Wt::WEnvironment& env) {
        return make_unique<HelloApplication>(env);
        });
}