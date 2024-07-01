if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/poeepadikada/newvesionpaid.git /newvesionpaid
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /newvesionpaid
fi
cd /newvesionpaid
pip3 install -U -r requirements.txt
echo "🚀Start⚡...."
python3 bot.py
