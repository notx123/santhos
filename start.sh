if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/notx123/santhos.git /notx123
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /notx123
fi
cd /notx123
pip3 install -U -r requirements.txt
echo "🚀Start⚡...."
python3 bot.py
